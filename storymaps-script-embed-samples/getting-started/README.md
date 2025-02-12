# Add a story to your domain and customize its link

Esri provides an easy way for developers to add ArcGIS StoryMaps stories to their own domains. This does not require you to download the story's source code or content. You will use a `<script>` tag to load the story in a simple HTML page on your organization's website, which enables you to establish your own URL for the story.

When using this method, you may continue to edit and republish the story in the ArcGIS StoryMaps builder.

This technique also enables you to customize the appearance and behavior of a story, but you can also embed the story as-is. For examples of the types of customizations you can do, see the other samples in this repo.

## Live sample

https://codepen.io/rdonihue/pen/oNKBboj

## Usage instructions

Implementing a custom domain involves:

- Create an index.html page or add the following to an existing HTML page
- add the embed-script id to your HTML page
- add your story id in the data-story-id=""
- host your HTML page

### HTML customizations

```html
<div class="storymaps-root"></div>
<script>
  id="embed-script"
  src="https://storymaps.arcgis.com/embed/view"
  data-story-id="1ba69ca9c31b4183b1ee486c36364198"
  data-root-node=".storymaps-root"
</script>
```
