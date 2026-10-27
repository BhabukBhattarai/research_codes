Study Area Asset

The script requires a study-area boundary asset imported into Google Earth Engine as table. The following code demonstrates how to filter the boundary to a specific district, using Sunsari District of Nepal as an example:

// IMPORT STUDY AREA
var dt = table.filter(ee.Filter.eq('DISTRICT', 'Sunsari'));
Map.addLayer(dt, {}, 'dt');

Replace 'Sunsari' with the name of your desired district, provided it matches the values in the DISTRICT attribute of the boundary dataset.

Data availability: The study-area boundary dataset used in this script will be provided upon request.
