# Font replacement

This sample demonstrates how to reference a self-hosted font file and replace the typefaces used within your story with the self-hosted fonts.

This is useful when you want the typefaces of your story to conform to the style guide and fonts used by your organization that may not be available by default in the ArcGIS StoryMaps builder.

> **Note:** See [this sample](/storymaps-script-embed-samples/splash-page/README.md#css-customizations) for an example of referencing a font from a font delivery service (Google Fonts/Adobe Fonts)

## Live sample

Default fonts             |  Custom fonts
:-------------------------:|:-------------------------:
![Default fonts](/storymaps-script-embed-samples/font-replacement/assets/example_default_fonts.png)  |  ![Custom Fonts](/storymaps-script-embed-samples/font-replacement/assets/example_custom_fonts.png)

[Click to see the live example](https://storymaps.esri.com/stories/storymaps-script-embed-examples/font-replacement/)

## Usage instructions

To implement custom fonts for your story, follow these steps:

- Self-host your desired font files or have access to a font delivery service.
- Load the font (see CSS customizations below)
- Define a global config object (`storyMapsEmbedConfig`)

### Defining storyMapsEmbedConfig

This object needs to be defined before the script embed tag:

```html
<!-- Embedded story -->
<div class="storymaps-root"></div>
<!-- Configure the story to use custom fonts you have loaded -->
<script>
  window.storyMapsEmbedConfig = {
    font: {
      title: {
        // Defining title is optional
        // If title is defined, all of it's properties are required
        fontFamily: "Permanent-Marker",
        weight: {
          normal: 400,
          bold: 700
        }
      },
      body: {
        // Defining body is optional
        // If body is defined, all of it's properties are required
        fontFamily: "Kalam",
        weight: {
          normal: 400,
          bold: 700
        }
      }
    }
  };
</script>
<!-- Load the story -->
<script
  id="embed-script"
  src="https://storymaps.arcgis.com/embed/view"
  data-story-id="<UPDATE_WITH_YOUR_STORY_ID>"
  data-root-node=".storymaps-root"
></script>
```

### CSS customizations

**Loading fonts from font delivery service**: If using a typeface from a font delivery service, you need to reference the font in the `<head>` of your HTML:

```html
<!-- Reference Google Fonts and CSS -->
<head>
  <link href="https://fonts.googleapis.com/css2?family=Sigmar&family=Sigmar+One&display=swap" rel="stylesheet" />
</head>
```

**Referencing self-hosted font files**: When using self-hosted fonts, reference them in your CSS file using `@font-face`, with their `src` as a relative URL to the file location on your web server:

```css
/* Reference self-hosted font files */
@font-face {
  font-family: "Permanent-Marker";
  src: url("./fonts/PermanentMarker/PermanentMarker-Regular.ttf") format("truetype");
}
@font-face {
  font-family: "Kalam";
  src: url("./fonts/Kalam/Kalam-Regular.ttf") format("truetype");
}
```
