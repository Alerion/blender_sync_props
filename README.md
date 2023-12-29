# Blender Sync Props Add-on

This Add-on allows you sync custom properties between View Layers and Object.
You can use this object properties in drivers and have different properties values
per View Layer.

## How to use

Add new View Layer to have at least two.

Create empty Object. It is our Control Object. Add custom properties.

Select Control Object in Add-on side panel.

![Select Control Object](./images/panel1.png?raw=true "Select Control Object")

Click "Sync Properties" or use Alt+Q.

Now properties with same names created for each View Layer.

Adjust properties values for each View Layer.

Click "Sync Properties" or use Alt+Q again. 
Next View Layer is selected and properties values are copied to Control Object properties.
Use these properties as Drivers.

See ``develop.blend`` scene as example.

## Notes

Inspired by [@redblueen](https://www.youtube.com/@redblueen).
