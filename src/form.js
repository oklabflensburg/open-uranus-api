const addVenueButton = document.querySelector('#addVenueButton')
const venueName = document.querySelector('#venueName')
const venueNameSuggestionList = document.querySelector(
  '#venueNameSuggestionList'
)
const addressFields = document.querySelector('#addressFields')

function toggleAddressFields() {
  addressFields.classList.toggle('hidden')
  addVenueButton.classList.toggle('hidden')
}

function updateVenueNameSuggestionList(venueNameSuggestions) {
  venueNameSuggestionList.innerHTML = ''

  if (venueNameSuggestions.length === 0) {
    addressFields.classList.add('hidden')
    addVenueButton.classList.add('hidden')

    return
  }

  venueNameSuggestions.forEach((item) => {
    const li = document.createElement('li')

    li.id = item.venue_id
    li.textContent = item.venue_name
    li.className =
      'px-4 py-2 cursor-pointer hover:bg-blue-500 hover:text-white'

    li.addEventListener('click', () => {
      fetchVenueById(item.venue_id)
      venueNameSuggestionList.classList.add('hidden')
      venueName.value = item.venue_name
    })

    venueNameSuggestionList.appendChild(li)
  })

  venueNameSuggestionList.classList.remove('hidden')
}

function toggleVenueNameListeners(enable) {
  const events = ['input', 'click']

  events.forEach((event) => {
    if (enable) {
      venueName.addEventListener(event, fetchVenueNameSuggestions)
    }
    else {
      venueName.removeEventListener(event, fetchVenueNameSuggestions)
    }
  })
}

async function fetchVenueById(id) {
  const url = `https://api.uranus.oklabflensburg.de/venue/id/?venue_id=${id}`

  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('Error fetching venue by id')
    }

    const data = await response.json()

    const venueFields = [
      { id: 'venueName', value: data.venue_name },
      { id: 'venueStreet', value: data.venue_street },
      { id: 'venueHouseNumber', value: data.venue_house_number },
      { id: 'venuePostalCode', value: data.venue_postal_code },
      { id: 'venueCity', value: data.venue_city }
    ]

    venueFields.forEach((field) => {
      const element = document.querySelector(`#${field.id}`)
      element.value = field.value
      element.disabled = true
      element.classList.add('bg-gray-100')
    })

    addressFields.classList.remove('hidden')
    addVenueButton.classList.remove('hidden')
  }
  catch (error) {
    console.error('Error:', error)
  }
}

async function fetchVenueNameSuggestions(e) {
  if (!e.target.value || e.target.value.length < 2) {
    venueNameSuggestionList.classList.add('hidden')
    venueNameSuggestionList.innerHTML = ''

    return
  }

  try {
    const response = await fetch(
      `https://api.uranus.oklabflensburg.de/venue/junk?query=${e.target.value}`
    )

    if (!response.ok) {
      throw new Error('Error fetching venue junk name venueNameSuggestions')
    }

    const data = await response.json()

    updateVenueNameSuggestionList(data || [])
  }
  catch (error) {
    console.error('Error:', error)
  }
}

addVenueButton.addEventListener('click', toggleAddressFields)
toggleVenueNameListeners(true)