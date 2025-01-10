# Custom header and footer

Does your organization employ a custom header and footer for its websites? It's a common approach to ensure a uniform web experience and simplify navigation across pages. By self-hosting your story, you can integrate a custom header and footer around your content, creating a seamless online experience for your audience.

## Live sample

[![Sample header footer](./assets/sample_header_footer.jpg "Sample header footer")](https://storymaps.esri.com/stories/storymaps-script-embed-examples/header-footer/)*[Click to see the live example](https://storymaps.esri.com/stories/storymaps-script-embed-examples/header-footer/)*

## Usage instructions

Implementing a customer header and footer involves:
- Creating a header element in your page.
- Creating a footer element in your page.
- Styling these elements.

### HTML customizations

**Header section** The header can contain site navigation or other links as required by your organization.
```html
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
```

**Footer section** This section can contain contact links and various other legal links as required by your organization.
```html
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
```
### CSS customizations

**Styling the header and footer** The header and footer of your webpage can be styled to align with branding elsewhere on your site.
```css
***REMOVED***/* Header Styles */
***REMOVED***header {
***REMOVED******REMOVED***background-color: #e46116;
***REMOVED******REMOVED***display: flex;
***REMOVED******REMOVED***align-items: center;
***REMOVED******REMOVED***justify-content: space-between;
***REMOVED******REMOVED***padding: 10px 20px;
***REMOVED******REMOVED***color: white;
***REMOVED******REMOVED***position: sticky;
***REMOVED******REMOVED***top: 0;
***REMOVED******REMOVED***z-index: 1000; /* Ensure it stays on top of other elements */
***REMOVED******REMOVED***box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Add shadow for better visibility */
***REMOVED******REMOVED***font-family: "Sigmar One";
***REMOVED***}
***REMOVED***
***REMOVED***.nav-tabs {
***REMOVED******REMOVED***display: flex;
***REMOVED******REMOVED***gap: 20px;
***REMOVED***}
***REMOVED***
***REMOVED***.nav-tabs a {
***REMOVED******REMOVED***color: white;
***REMOVED******REMOVED***text-decoration: none;
***REMOVED******REMOVED***font-size: 16px;
***REMOVED***}
***REMOVED***
***REMOVED***.nav-tabs a:hover {
***REMOVED******REMOVED***text-decoration: underline;
***REMOVED***}

***REMOVED***/* Footer Styles */
***REMOVED***footer {
***REMOVED******REMOVED***background-color: #e46116;
***REMOVED******REMOVED***color: white;
***REMOVED******REMOVED***padding: 20px;
***REMOVED******REMOVED***text-align: center;
***REMOVED***}
***REMOVED***
***REMOVED***footer a {
***REMOVED******REMOVED***color: white;
***REMOVED******REMOVED***text-decoration: none;
***REMOVED******REMOVED***margin: 0 15px;
***REMOVED***}
***REMOVED***
***REMOVED***footer a:hover {
***REMOVED******REMOVED***text-decoration: underline;
***REMOVED***}
```
