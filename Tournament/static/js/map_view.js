// Инициализация карты Яндекс с использованием атрибутов HTML элемента.
// Устанавливает центр карты, уровень масштабирования и добавляет метку.
ymaps.ready(init);

function init() {
    const mapElement = document.getElementById("map");
    if (mapElement) {
        // Получение данных из атрибутов
        const latRaw = mapElement.getAttribute("data-lat").replace(',', '.');
        const lonRaw = mapElement.getAttribute("data-lon").replace(',', '.');
        const zoomRaw = mapElement.getAttribute("data-zoom");
        const centerLatRaw = mapElement.getAttribute("data-center-lat").replace(',', '.');
        const centerLonRaw = mapElement.getAttribute("data-center-lon").replace(',', '.');

        console.log("Raw Map attributes:", { latRaw, lonRaw, zoomRaw, centerLatRaw, centerLonRaw });

        // Преобразование данных в числа
        const lat = parseFloat(latRaw);
        const lon = parseFloat(lonRaw);
        const zoom = parseInt(zoomRaw, 10);
        const centerLat = parseFloat(centerLatRaw);
        const centerLon = parseFloat(centerLonRaw);

        console.log("Parsed Map attributes:", { lat, lon, zoom, centerLat, centerLon });

        const mapCenter = (!isNaN(centerLat) && !isNaN(centerLon)) ? [centerLat, centerLon] : [lat, lon];
        console.log("Map center coordinates:", mapCenter);

        const myMap = new ymaps.Map("map", {
            center: mapCenter,
            zoom: zoom,
            controls: ['geolocationControl', 'searchControl']
        });

        console.log("Map initialized with center and zoom:", myMap.getCenter(), myMap.getZoom());

        if (!isNaN(lat) && !isNaN(lon)) {
            const placemark = new ymaps.Placemark([lat, lon], {}, {
                preset: 'islands#redDotIconWithCaption'
            });
            myMap.geoObjects.add(placemark);
            console.log("Placemark added at coordinates:", [lat, lon]);
        } else {
            console.error("Invalid placemark coordinates");
        }
    } else {
        console.error("Map element not found");
    }
}
