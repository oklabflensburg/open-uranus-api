import L from 'leaflet'
import 'leaflet.markercluster'

import 'leaflet/dist/leaflet.css'

import markerDefault from 'url:../static/marker-icon-default.webp'
import markerSelected from 'url:../static/marker-icon-active.webp'

import { Env } from './env.js'


const env = new Env()
env.injectLinkContent('.contact-mail', 'mailto:', '', env.contactMail, 'E-Mail')


const defaultIcon = L.icon({
  iconUrl: markerDefault,
  iconSize: [30, 36],
  iconAnchor: [15, 36],
  tooltipAnchor: [0, -37]
})


const selectedIcon = L.icon({
  iconUrl: markerSelected,
  iconSize: [30, 36],
  iconAnchor: [15, 36],
  tooltipAnchor: [0, -37]
})

// Store markers by slug
const markerMap = new Map()

// Flag to ensure fitBounds is called only once
let isBoundsSet = false
let previousSelectedMarker = null
let currentLayer = null

const center = [54.79443515, 9.43205485]
const zoomLevelInitial = 13
const addItemsByBounds = false

const markerClusterGroup = L.markerClusterGroup({
  zoomToBoundsOnClick: true,
  disableClusteringAtZoom: 18
})

const map = L.map('map', {
  zoomControl: false
}).setView(center, zoomLevelInitial)


let zoomControl = L.control.zoom({
  position: 'bottomright'
}).addTo(map)


function updateScreen(screen) {
  const title = 'Veranstaltung finden - Uranus Venue Map'

  if (screen === 'home') {
    document.title = title
    document.querySelector('meta[property="og:title"]').setAttribute('content', title)
  }
  else {
    document.title = `${screen} - ${title}`
    document.querySelector('meta[property="og:title"]').setAttribute('content', `${screen} - ${title}`)
  }
}


function fetchBlob(url, designation) {
  if (!url || typeof url !== 'string') {
    console.error('Invalid URL passed to fetchBlob:', url)
    return
  }

  fetch(url, { method: 'get', mode: 'cors' })
    .then((response) => {
      if (!response.ok) {
        console.warn(`${url} returned HTTP status code ${response.status}`)
        return null
      }
      return response.blob()
    })
    .then((blob) => {
      if (!blob) {
        console.error('Failed to retrieve image blob from response')
        return
      }

      const imageUrl = URL.createObjectURL(blob)
      const imageElement = document.createElement('img')
      imageElement.src = imageUrl
      imageElement.setAttribute('alt', designation || 'Denkmalschutz')

      const divElement = document.createElement('div')
      divElement.classList.add('px-3', 'py-2', 'w-full', 'text-xs', 'text-gray-100', 'bg-gray-600')
      divElement.innerText = 'Foto © Landesamt für Denkmalpflege'

      const container = document.querySelector('#detailImage')

      if (!container) {
        console.error('Element #detailImage not found')
        return
      }

      container.appendChild(imageElement)
      container.appendChild(divElement)
    })
    .catch((error) => console.error('Error in fetchBlob:', error))
}


function capitalizeEachWord(str) {
  return str.replace(/-/g, ' ').replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  })
}


function isValidUrl(string) {
  try {
    const url = new URL(string)
    return url.protocol === 'http:' || url.protocol === 'https:'
  }
  catch (_) {
    return false
  }
}


function renderItemMeta(data) {
  const venueId = data.venue_id
  const venueName = data.venue_name
  const venueType = data.venue_type
  const street = data.street
  const houseNumber = data.house_number
  const postalCode = data.postal_code
  const city = data.city
  const countryCode = data.country_code
  const openedAt = data.opened_at
  const closedAt = data.closed_at
  const organizerName = data.organizer_name
  const organizerURL	= data.organizer_url

  const title = 'Open Uranus Venue Map'
  /* const title = `${capitalizeEachWord(slug)} - Digitale Denkmalkarte`

  document.querySelector('title').innerHTML = title
  document.querySelector('meta[property="og:title"]').setAttribute('content', title)
  document.querySelector('meta[property="og:url"]').setAttribute('content', `${window.location.href}${slug}`) */

  let detailOutput = ''

  detailOutput += `<li class="pb-2 text-xl lg:text-2xl"><strong>${venueName}</strong></li>`
  detailOutput += `<li class="last-of-type:pb-2 py-1 mb-3">${street} ${houseNumber}<br>${postalCode} ${city}</li>`

  if (organizerName) {
    detailOutput += `<li class="last-of-type:pb-2 pt-2"><strong>organizerName</strong><br>${organizerName}</li>`
  }

  if (organizerURL) {
    detailOutput += `<li class="last-of-type:pb-2 pt-2"><strong>organizerURL</strong><br>${organizerURL}</li>`
  }

  detailOutput += `<li class="last-of-type:pb-2 pt-2"><strong>openedAt</strong><br>${openedAt}</li>`
  detailOutput += `<li class="pt-2"><strong>closedAt</strong><br>${closedAt}</li>`

  const detailList = document.querySelector('#detailList')

  document.querySelector('title').innerHTML = title
  document.querySelector('meta[property="og:title"]').setAttribute('content', title)

  detailList.innerHTML = detailOutput
  document.querySelector('#about').classList.add('hidden')
  document.querySelector('#sidebar').classList.add('absolute')
  document.querySelector('#sidebar').classList.remove('hidden')
  document.querySelector('#sidebarContent').classList.remove('hidden')
  document.querySelector('#sidebarCloseWrapper').classList.remove('block')
}


function cleanItemMeta() {
  document.querySelector('#detailList').innerHTML = ''
  document.querySelector('#detailImage').innerHTML = ''
  document.querySelector('#sidebar').classList.add('hidden')
  document.querySelector('#sidebar').classList.remove('absolute')
  document.querySelector('#about').classList.remove('hidden')
  document.querySelector('#sidebarContent').classList.add('hidden')
}


async function fetchJsonData(url) {
  try {
    const response = await fetch(url, { method: 'GET' })

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    return await response.json()
  }
  catch (error) {
    console.error('Fetch error:', error)

    return null
  }
}


async function fetchItemDetailBySlug(slug) {
  const url = `https://api.uranus.oklabflensburg.de/monument/v1/detail?slug=${slug}`

  const data = await fetchJsonData(url)
  const zoomLevelDetail = 17

  const geoJsonData = {
    'type': 'FeatureCollection',
    'features': [{
      'type': 'Feature',
      'id': data['id'],
      'geometry': {
        'type': data['geojson']['type'],
        'coordinates': data['geojson']['coordinates']
      },
      'properties': {
        'label': data['label'],
        'slug': data['slug']
      }
    }]
  }

  if (isValidUrl(data.image_url)) {
    document.querySelector('#detailImage').innerHTML = ''
    fetchBlob(data.image_url, data.designation)
  }

  renderItemMeta(data)
  addItemsToMap(geoJsonData, true, zoomLevelDetail)

  const matchingMarker = findMarkerById(data['id'])

  if (matchingMarker) {
    setSelectedMarker(matchingMarker)
  }
}


async function fetchItemDetailById(id) {
  const url = `https://api.uranus.oklabflensburg.de/event/?venue_id=${id}`
  const listResultsContainer = document.querySelector('#listResults')
  const listContainer = document.querySelector('#list')
  const mapContainer = document.querySelector('#map')
  const response = await fetch(url)

  if (!response.ok) {
    mapContainer.classList.remove('hidden')
    listContainer.classList.add('hidden')
    listResultsContainer.innerHTML = ''
    throw new Error(`HTTP error! Status: ${response.status}`)
  }

  const eventObjects = await response.json()
  mapContainer.classList.add('hidden')
  listContainer.classList.remove('hidden')
  listResultsContainer.innerHTML = ''

  eventObjects.forEach((eventObject) => listResultsContainer.appendChild(createEventCard(eventObject)))
}


async function fetchItemPointsByBounds() {
  const bounds = map.getBounds()
  const bbox = {
    xmin: bounds.getWest(),
    ymin: bounds.getSouth(),
    xmax: bounds.getEast(),
    ymax: bounds.getNorth()
  }

  const url = `https://api.uranus.oklabflensburg.de/venue/bounds?xmin=${bbox.xmin}&ymin=${bbox.ymin}&xmax=${bbox.xmax}&ymax=${bbox.ymax}`

  const data = await fetchJsonData(url)

  addItemsToMap(data, addItemsByBounds, zoomLevelInitial)
}


function addItemsToMap(data, fetchAdditionalItems, zoomLevel) {
  // Remove the existing layer
  if (currentLayer !== null) {
    currentLayer.removeLayer(currentLayer)
  }
  else {
    currentLayer = markerClusterGroup
  }

  const geojsonGroup = L.geoJSON(data, {
    onEachFeature(feature, layer) {
      const id = feature.id

      // Store marker reference in markerMap
      markerMap.set(id, layer)

      layer.on('click', async function (e) {
        cleanItemMeta()

        if (!e || !e.target || !e.target.feature) {
          console.error('Invalid event object:', e)
          return
        }

        await fetchItemDetailById(id)

        // Set selected icon when a marker is clicked
        setSelectedMarker(e.target)
      })
    },
    pointToLayer(feature, latlng) {
      return L.marker(latlng, { icon: defaultIcon })
        .bindTooltip(feature.properties.label, { permanent: false, direction: 'top' })
        .openTooltip()
    }
  })

  currentLayer.addLayer(geojsonGroup)
  map.addLayer(currentLayer)

  // Fit map bounds
  if (!isBoundsSet) {
    map.fitBounds(currentLayer.getBounds(), { maxZoom: zoomLevel })
    isBoundsSet = true
  }
}


function handleWindowSize() {
  const innerWidth = window.innerWidth

  if (innerWidth >= 1024) {
    map.removeControl(zoomControl)

    zoomControl = L.control.zoom({
      position: 'topleft'
    }).addTo(map)
  }
  else {
    map.removeControl(zoomControl)
  }
}


// Find marker by slug
function findMarkerById(slug) {
  return markerMap.get(slug) || null
}


// Set the selected marker
function setSelectedMarker(marker) {
  if (previousSelectedMarker !== null) {
    previousSelectedMarker.setIcon(defaultIcon) // Reset previous marker
  }

  marker.setIcon(selectedIcon)
  previousSelectedMarker = marker
}


// Function to handle navigation changes
function navigateTo(screen, updateHistory = true) {
  const currentState = history.state

  // Avoid pushing a duplicate entry
  if (currentState && currentState.screen === screen) {
    return
  }

  if (updateHistory) {
    history.pushState({ screen }, '', screen === 'home' ? '/' : `/${screen}`)
  }

  updateScreen(screen)
}


function renderTags(tags, baseClasses, hoverClasses) {
  if (!Array.isArray(tags)) {
    tags = [tags]
  }

  return tags.map((tag) => {
    const span = document.createElement('span')
    span.className = `font-sans text-xs font-medium px-2.5 py-1 rounded ${baseClasses} ${hoverClasses}`
    span.textContent = tag
    return span
  })
}


function formatDateToGerman(dateString) {
  const date = new Date(dateString)

  if (!isNaN(date)) {
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()

    return `${day}.${month}.${year}`
  }

  return dateString // Return original if invalid
}


function createEventCard(eventObject) {
  const card = document.createElement('div')
  card.className = 'bg-white rounded-lg shadow-lg p-4 mb-4 hover:shadow-xl transition-shadow'

  // Title
  const title = document.createElement('h3')
  title.className = 'text-lg lg:text-2xl font-semibold mb-2'
  title.textContent = `${formatDateToGerman(eventObject.event_date_start)} - ${eventObject.event_title}`

  // Description
  const description = document.createElement('p')
  description.className = 'text-md text-gray-600 mb-3'
  description.textContent = eventObject.event_description

  // Info Container
  const infoContainer = document.createElement('div')
  infoContainer.className = 'text-md text-gray-600 text-sm space-y-1 mb-1'

  // Location
  const location = document.createElement('p')
  location.innerHTML = `<strong>📍 Ort:</strong> ${eventObject.venue_name} (${eventObject.venue_city}, ${eventObject.venue_postcode})`

  // Calendar Link
  const calendarLink = document.createElement('p')
  const calendarAnchor = document.createElement('a')
  calendarAnchor.href = 'event.ics'
  calendarAnchor.download = ''
  calendarAnchor.className = 'inline-flex items-center text-blue-500 hover:text-pink-700 focus:text-pink-700 px-2 py-1 transition'
  calendarAnchor.textContent = '📅 Termin in Kalender speichern'
  calendarLink.appendChild(calendarAnchor)

  // Organizer
  const organizer = document.createElement('p')
  organizer.innerHTML = `<strong>🎟 Veranstalter:</strong> ${eventObject.organizer_name}`

  // Append all info elements
  infoContainer.append(location, calendarLink, organizer)

  // Tags Container
  const tagContainer = document.createElement('div')
  tagContainer.className = 'flex flex-wrap gap-2 mt-2'

  tagContainer.append(
    ...renderTags(eventObject.venue_type, 'bg-orange-100 text-orange-800', 'hover:bg-orange-500 hover:text-white'),
    ...renderTags(eventObject.event_type, 'bg-pink-100 text-pink-800', 'hover:bg-pink-500 hover:text-white'),
    ...renderTags(eventObject.genre_type, 'bg-blue-100 text-blue-800', 'hover:bg-blue-500 hover:text-white')
  )

  // Append elements to card
  card.append(title, description, infoContainer, tagContainer)
  return card
}




function buildEventUrl({ city, postcode, venueTypeId, genreTypeId, spaceTypeId, eventTypeId, dateStart, dateEnd }) {
  const baseUrl = 'https://api.uranus.oklabflensburg.de/event/'
  const params = new URLSearchParams()

  const filters = {
    city,
    postal_code: postcode,
    venue_type_id: venueTypeId,
    genre_type_id: genreTypeId,
    space_type_id: spaceTypeId,
    event_type_id: eventTypeId,
    date_start: dateStart ? `>=${formatDateToGerman(dateStart)}` : null,
    date_end: dateEnd ? `<=${formatDateToGerman(dateEnd)}` : null
  }

  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.append(key, value)
    }
  })

  return params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl
}



async function handleFormChange() {
  const city = document.querySelector('#venueCity').value || null
  const postcode = document.querySelector('#venuePostcode').value || null
  const spaceTypeId = document.querySelector('#spaceType').value || null
  const venueTypeId = document.querySelector('#venueType').value || null
  const genreTypeId = document.querySelector('#genreType').value || null
  const eventTypeId = document.querySelector('#eventType').value || null
  const dateStart = document.querySelector('#eventDateStart').value || null
  const dateEnd = document.querySelector('#eventDateEnd').value || null

  const url = buildEventUrl({ city, postcode, spaceTypeId, venueTypeId, genreTypeId, eventTypeId, dateStart, dateEnd })

  try {
    const listResultsContainer = document.querySelector('#listResults')
    const listContainer = document.querySelector('#list')
    const mapContainer = document.querySelector('#map')
    const response = await fetch(url)

    if (!response.ok) {
      mapContainer.classList.remove('hidden')
      listContainer.classList.add('hidden')
      listResultsContainer.innerHTML = ''
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const eventObjects = await response.json()
    mapContainer.classList.add('hidden')
    listContainer.classList.remove('hidden')
    listResultsContainer.innerHTML = ''

    eventObjects.forEach((eventObject) => listResultsContainer.appendChild(createEventCard(eventObject)))
  }
  catch (error) {
    console.error('Error fetching events:', error)
  }
}



async function fetchAndPopulate(url, elementId, idKey, nameKey) {
  try {
    const response = await fetch(url)
    const data = await response.json()
    const selectElement = document.getElementById(elementId)
    selectElement.innerHTML = '<option selected value>Bitte auswählen</option>'
    selectElement.innerHTML += data.map((item) => `<option class="cursor-pointer" value="${item[idKey]}">${item[nameKey]}</option>`).join('')
  }
  catch (error) {
    console.error(`Error fetching ${elementId}:`, error)
  }
}

document.addEventListener('DOMContentLoaded', () => {
  fetchAndPopulate('https://api.uranus.oklabflensburg.de/event/type/', 'eventType', 'event_type_id', 'event_type_name')
  fetchAndPopulate('https://api.uranus.oklabflensburg.de/venue/type/', 'venueType', 'venue_type_id', 'venue_type_name')
  fetchAndPopulate('https://api.uranus.oklabflensburg.de/space/type/', 'spaceType', 'space_type_id', 'space_type_name')
  fetchAndPopulate('https://api.uranus.oklabflensburg.de/genre/type/', 'genreType', 'genre_type_id', 'genre_type_name')
})


document.querySelector('#eventForm').addEventListener('input', handleFormChange)
document.querySelector('#eventForm').addEventListener('change', handleFormChange)


// Handle initial page load
window.onload = () => {
  // Initialize the map and handle events after DOM is ready
  L.tileLayer('https://tiles.oklabflensburg.de/sgm/{z}/{x}/{y}.png', {
    maxZoom: 20,
    tileSize: 256,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="dc:rights">OpenStreetMap</a> contributors'
  }).addTo(map)

  // Attach event listeners
  map.on('moveend', fetchItemPointsByBounds)
  map.on('click', cleanItemMeta)

  // Sidebar close button handler
  document.querySelector('#sidebarCloseButton').addEventListener('click', function (e) {
    e.preventDefault()
    cleanItemMeta()
  })

  // Get the current path and determine screen
  const path = decodeURIComponent(window.location.pathname)
  const screen = path === '/' ? 'home' : path.slice(1) // Remove leading "/"

  // Ensure history state is set correctly
  if (!history.state) {
    history.replaceState({ screen }, '', path)
  }

  updateScreen(screen)

  // Load content based on the screen
  if (screen === 'home') {
    fetchItemPointsByBounds()
  }
  else {
    fetchItemDetailBySlug(screen)
  }
}

// Handle back/forward button navigation
window.addEventListener('popstate', (event) => {
  // If event.state exists, use it; otherwise, determine from pathname
  const screen = event.state && event.state.screen ? event.state.screen : 'home'

  if (screen === 'home') {
    cleanItemMeta()
    fetchItemPointsByBounds()
  }
  else {
    fetchItemDetailBySlug(screen)
  }
})


// Attach the resize event listener, but ensure proper function reference
window.addEventListener('resize', handleWindowSize)

// Trigger the function initially to handle the initial screen size
handleWindowSize()