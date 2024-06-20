// Инициализация карты Яндекс с использованием значений из HTML элементов.
// Устанавливает начальный центр карты, уровень масштабирования и добавляет метку.
// Сохраняет изменения центра и масштаба карты, обновляет адрес при клике и поиске.
ymaps.ready(init);

function init() {
    var initialCenter = [55.76, 37.64];
    var initialZoom = 10;

    var mapCenterInput = document.getElementById('mapCenter');
    var mapZoomInput = document.getElementById('mapZoom');
    var selectedLocationInput = document.getElementById('selectedLocation');
    var addressInput = document.getElementById('display_address');
    var hiddenAddressInput = document.getElementById('hidden_address');

    // Проверка сохранённых значений
    if (mapCenterInput.value) {
        var savedCenter = mapCenterInput.value.split(',');
        if (savedCenter.length === 2) {
            initialCenter = [parseFloat(savedCenter[0]), parseFloat(savedCenter[1])];
        }
    }

    if (mapZoomInput.value) {
        initialZoom = parseInt(mapZoomInput.value, 10);
    }

    var myMap = new ymaps.Map("map", {
        center: initialCenter,
        zoom: initialZoom,
        controls: ['geolocationControl', 'searchControl']
    });

    var placemark;

    // Если есть сохранённые координаты метки, добавляем её на карту
    if (selectedLocationInput.value) {
        var savedCoords = selectedLocationInput.value.split(',');
        if (savedCoords.length === 2) {
            var coords = [parseFloat(savedCoords[0]), parseFloat(savedCoords[1])];
            placemark = new ymaps.Placemark(coords, {}, {
                preset: 'islands#redDotIconWithCaption'
            });
            myMap.geoObjects.add(placemark);

            // Обновление адреса для сохранённых координат
            ymaps.geocode(coords).then(function(res) {
                var firstGeoObject = res.geoObjects.get(0);
                var address = firstGeoObject.getAddressLine();
                addressInput.value = address;
                hiddenAddressInput.value = address;
            });
        }
    }

    // Сохранение начальных координат и уровня масштабирования
    mapZoomInput.value = myMap.getZoom();
    mapCenterInput.value = myMap.getCenter().join(',');

    myMap.events.add('boundschange', function(event) {
        if (event.get('newCenter')) {
            mapCenterInput.value = event.get('newCenter').join(',');
        }
        if (event.get('newZoom') !== event.get('oldZoom')) {
            mapZoomInput.value = event.get('newZoom');
        }
    });

    myMap.events.add('click', function(e) {
        var coords = e.get('coords');

        if (placemark) {
            placemark.geometry.setCoordinates(coords);
        } else {
            placemark = new ymaps.Placemark(coords, {}, {
                preset: 'islands#redDotIconWithCaption'
            });
            myMap.geoObjects.add(placemark);
        }

        selectedLocationInput.value = coords.join(',');

        ymaps.geocode(coords).then(function(res) {
            var firstGeoObject = res.geoObjects.get(0);
            var address = firstGeoObject.getAddressLine();
            addressInput.value = address;
            hiddenAddressInput.value = address;
        });
    });

    var searchControl = myMap.controls.get('searchControl');
    searchControl.events.add('resultselect', function(e) {
        var index = e.get('index');
        searchControl.getResult(index).then(function(res) {
            var coords = res.geometry.getCoordinates();
            if (placemark) {
                placemark.geometry.setCoordinates(coords);
            } else {
                placemark = new ymaps.Placemark(coords, {}, {
                    preset: 'islands#redDotIconWithCaption'
                });
                myMap.geoObjects.add(placemark);
            }
            selectedLocationInput.value = coords.join(',');

            ymaps.geocode(coords).then(function(res) {
                var firstGeoObject = res.geoObjects.get(0);
                var address = firstGeoObject.getAddressLine();
                addressInput.value = address;
                hiddenAddressInput.value = address;
            });
        });
    });
}
