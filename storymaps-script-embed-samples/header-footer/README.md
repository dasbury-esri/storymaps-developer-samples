# Custom header and footer

Does your organization employ a custom header and footer for its websites? It's a common approach to ensure a uniform web experience and simplify navigation across pages. By self-hosting your story, you can integrate a custom header and footer around your content, creating a seamless online experience for your audience.

## Live sample

[![Sample header footer](./assets/sample_header_footer.jpg "Sample header footer")](https://storymaps.esri.com/stories/storymaps-script-embed-examples/header-footer/)_[Click to see the live example](https://storymaps.esri.com/stories/storymaps-script-embed-examples/header-footer/)_

## Usage instructions

Implementing a customer header and footer involves:

- Creating a header element in your page.
- Creating a footer element in your page.
- Styling these elements.
- Passing the height of your header to the Story.

### HTML customizations

**Header section** The header can contain site navigation or other links as required by your organization.

```html
<!-- Header Section -->
<header>
  <!-- Logo as SVG -->
  <div class="logo">
    <!-- Simple SVG logo (you can replace this with any other SVG code) -->
    <a href="/"><img src="./rex_skull.svg" height="50-px" alt="My company home" /></a>
  </div>

  <!-- Navigation Tabs -->
  <nav class="nav-tabs">
    <a href="#home">Home</a>
    <a href="#about">About</a>
    <a href="#services">Services</a>
    <a href="#contact">Contact</a>
  </nav>
</header>
```

**Footer section** This section can contain contact links and various other legal links as required by your organization.

```html
<!-- Footer Section -->
<footer>
  <p>&copy; 2024 Your Company Name. All rights reserved.</p>
  <a href="#privacy-policy">Privacy Policy</a>
  <a href="#terms-of-service">Terms of Service</a>
  <a href="#contact">Contact Us</a>
</footer>
```

### CSS customizations

**Styling the header and footer** The header and footer of your webpage can be styled to align with branding elsewhere on your site.

```css
body {
  --primary-background-color: #e46116;
  --primary-text-color: white;
}
/* Header Styles */
header {
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  height: 48px;
  color: var(--primary-text-color);
  position: sticky;
  top: 0;
  z-index: 1; /* Ensure it stays on top of other elements in the Story */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Add shadow for better visibility */
  font-family: "Sigmar One";
}

.nav-tabs {
  display: flex;
  gap: 20px;
}

.nav-tabs a {
  color: var(--primary-text-color);
  text-decoration: none;
  font-size: 16px;
}

.nav-tabs a:hover {
  text-decoration: underline;
}

/* Footer Styles */
footer,
footer a {
  color: var(--primary-text-color);
}

footer {
  background-color: var(--primary-color);
  padding: 20px;
  text-align: center;
}

footer a {
  text-decoration: none;
  margin: 0 15px;
}

footer a:hover {
  text-decoration: underline;
}
```

### Configure and initialize the Story

NOTE: To ensure the proper functionality of various UI components within a Story, such as a Sidecar, it is essential to define a storyMapsEmbedConfig object that includes your headers' height to facilitate seamless integration

```html
<!-- Pass the height of your custom header to the Story config object -->
<script>
  window.storyMapsEmbedConfig = {
    topOffset: '48px';
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
