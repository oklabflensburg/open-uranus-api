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
const addMonumentsByBounds = false

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


function renderMonumentMeta(data) {
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


function cleanMonumentMeta() {
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


async function fetchMonumentDetailBySlug(slug) {
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

  renderMonumentMeta(data)
  addMonumentsToMap(geoJsonData, true, zoomLevelDetail)

  const matchingMarker = findMarkerById(data['id'])

  if (matchingMarker) {
    setSelectedMarker(matchingMarker)
  }
}


async function fetchMonumentDetailById(id) {
  const url = `https://api.uranus.oklabflensburg.de/venue/id?venue_id=${id}`

  const data = await fetchJsonData(url)
  const zoomLevelDetail = 17

  const geoJsonData = {
    'type': 'FeatureCollection',
    'features': [{
      'type': 'Feature',
      'venue_id': data['venue_id'],
      'geometry': {
        'type': data['geojson']['type'],
        'coordinates': data['geojson']['coordinates']
      },
      'properties': {
        'venue_name': data['venue_name']
      }
    }]
  }

  renderMonumentMeta(data)
  addMonumentsToMap(geoJsonData, addMonumentsByBounds, zoomLevelDetail)


  const matchingMarker = findMarkerById(data['venue_id'])

  if (matchingMarker) {
    setSelectedMarker(matchingMarker)
  }
}


// https://api.oklabflensburg.de/monument/v1/geometries
async function fetchMonumentPointsByBounds() {
  const bounds = map.getBounds()
  const bbox = {
    xmin: bounds.getWest(),
    ymin: bounds.getSouth(),
    xmax: bounds.getEast(),
    ymax: bounds.getNorth()
  }

  const url = `https://api.uranus.oklabflensburg.de/venue/bounds?xmin=${bbox.xmin}&ymin=${bbox.ymin}&xmax=${bbox.xmax}&ymax=${bbox.ymax}`

  const data = await fetchJsonData(url)

  addMonumentsToMap(data, addMonumentsByBounds, zoomLevelInitial)
}


function addMonumentsToMap(data, fetchAdditionalMonuments, zoomLevel) {
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
        cleanMonumentMeta()

        if (!e || !e.target || !e.target.feature) {
          console.error('Invalid event object:', e)
          return
        }

        await fetchMonumentDetailById(id)

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


document.querySelector('#eventForm').addEventListener('submit', async function (event) {
  event.preventDefault()

  const city = document.querySelector('#venueCity').value || null
  const postcode = document.querySelector('#venuePostcode').value || null
  const spaceTypeId = document.querySelector('#spaceType').value || null
  const venueTypeId = document.querySelector('#venueType').value || null
  const genreTypeId = document.querySelector('#genreType').value || null
  const eventTypeId = document.querySelector('#eventType').value || null
  const dateStart = document.querySelector('#eventDateStart').value || null
  const dateEnd = document.querySelector('#eventDateEnd').value || null

  const baseUrl = 'https://api.uranus.oklabflensburg.de/event/'
  let url = baseUrl

  const params = []

  if (city) {
    params.push(`city=${city}`)
  }

  if (postcode) {
    params.push(`postal_code=${postcode}`)
  }

  if (venueTypeId) {
    params.push(`venue_type_id=${venueTypeId}`)
  }

  if (genreTypeId) {
    params.push(`genre_type_id=${genreTypeId}`)
  }

  if (spaceTypeId) {
    params.push(`space_type_id=${spaceTypeId}`)
  }

  if (eventTypeId) {
    params.push(`event_type_id=${eventTypeId}`)
  }

  if (dateStart) {
    params.push(`date_start=${dateStart}`)
  }

  if (dateEnd) {
    params.push(`date_end=${dateEnd}`)
  }

  if (params.length > 0) {
    const urlParams = params.join('&')
    url = `${baseUrl}?${urlParams}`
  }

  console.log(url)

  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const events = await response.json()

    const listContainer = document.querySelector('#list')
    const mapContainer = document.querySelector('#map')
    mapContainer.classList.add('hidden')
    listContainer.classList.remove('hidden')

    document.querySelector('#listResults').innerHTML = events.map((e) => `
<div class="bg-white rounded-lg shadow-lg p-4 mb-4 hover:shadow-xl transition-shadow">
    <h3 class="text-xl font-semibold text-blue-600 mb-2">${e.event_title}</h3>
    <p class="text-gray-700 mb-3">${e.event_description}</p>
    <div class="text-gray-600 text-sm space-y-1">
        <p><strong>📍 Ort:</strong> ${e.venue_name} (${e.venue_city}, ${e.venue_postcode})</p>
        <p><strong>📅 Datum:</strong> ${new Date(e.event_date_start).toLocaleDateString()}</p>
        <p><strong>🎟 Veranstalter:</strong> ${e.organizer_name}</p>
    </div>
</div>
                `).join('')
  }
  catch (error) {
    console.error('Error fetching events:', error)
  }
})



// Handle initial page load
window.onload = () => {
  // Initialize the map and handle events after DOM is ready
  L.tileLayer('https://tiles.oklabflensburg.de/sgm/{z}/{x}/{y}.png', {
    maxZoom: 20,
    tileSize: 256,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="dc:rights">OpenStreetMap</a> contributors'
  }).addTo(map)

  // Attach event listeners
  map.on('moveend', fetchMonumentPointsByBounds)
  map.on('click', cleanMonumentMeta)

  // Sidebar close button handler
  document.querySelector('#sidebarCloseButton').addEventListener('click', function (e) {
    e.preventDefault()
    cleanMonumentMeta()
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
    fetchMonumentPointsByBounds()
  }
  else {
    fetchMonumentDetailBySlug(screen)
  }
}

// Handle back/forward button navigation
window.addEventListener('popstate', (event) => {
  // If event.state exists, use it; otherwise, determine from pathname
  const screen = event.state && event.state.screen ? event.state.screen : 'home'

  if (screen === 'home') {
    cleanMonumentMeta()
    fetchMonumentPointsByBounds()
  }
  else {
    fetchMonumentDetailBySlug(screen)
  }
})


// Attach the resize event listener, but ensure proper function reference
window.addEventListener('resize', handleWindowSize)

// Trigger the function initially to handle the initial screen size
handleWindowSize()