# Splash screen

You may want to greet readers or preface the story they're about to read. A splash screen can perform this role and sit atop your story until dismissed.

## Live sample

[![Splash screen sample codepen](./assets/sample_splash_screen.jpg "Splash screen sample codepen")](https://codepen.io/Warren-Davison/pen/abeNewB)*[Click to see the live codepen](https://codepen.io/Warren-Davison/pen/abeNewB)*


## Usage instructions

Implementing a splash screen involves:
- Creating a `<div class="splash-overlay">` in the HTML page that obscures the main content of the page.
- Creating a `<div class="splash-screen">` in the HTML page that contains the text and button that will greet your readers.
- Define a `closeSplashScreen()` function in the HTML page, called by the button that hides the `.splash-overlay`.
- Define the appearance of the `.splash-overlay` and `.splash-screen` classes in the CSS file.
- Prevent the main content of the page from scrolling until **the splash screen is dismissed** by adding `overflow: hidden` to the CSS of the `***REMOVED***`.

### HTML snippets

**Prevent the story from scrolling**: This prevents the story from scrolling when the splash screen is active.
```html
<!-- Prevent the story from scrolling-->
***REMOVED***
```

**Splash screen and overlay**: These elements make up the `splash screen` that contains the greeting and a `splash-overlay` that obscures the story underneath.
```html
<!-- Splash overlay -->
<div class="splash-overlay" id="splashOverlay">
<!-- Splash screen -->
<div class="splash-screen">
***REMOVED******REMOVED***<img src="rex_skull.svg" height="50-px" alt="T-Rex Fossil">
***REMOVED******REMOVED***<h1>Welcome to Our Dino Dig!</h1>
***REMOVED******REMOVED***<p>Since dinosaurs have been extinct for millions of years, we’ll become paleontologists to excavate the fossilized remains of these prehistoric giants.</p>
***REMOVED******REMOVED***<p>Are you ready to get your hands dirty?</p>
***REMOVED******REMOVED***<button onclick="closeSplashScreen()">Yeah, I can dig it!</button>
</div>
</div>
```

**Dismissing the splash screen**: This defines a `closeSplashScreen()` function that is called by the button within the `<div class="splash-screen">` that:
- Hides the `<div class="splash-screen">` and all of its contents by setting `display = 'none'`.
- Enables scrolling by removing the `no-scroll` class from the `***REMOVED***`.
```html
***REMOVED***<script>
***REMOVED******REMOVED***// Function to close the splash screen and reveal the story
***REMOVED******REMOVED***function closeSplashScreen() {
***REMOVED******REMOVED******REMOVED***// Hide the splash screen
***REMOVED******REMOVED******REMOVED***document.getElementById('splashOverlay').style.display = 'none';

***REMOVED******REMOVED******REMOVED***// Enable scrolling on the main page
***REMOVED******REMOVED******REMOVED***document.body.classList.remove('no-scroll');
***REMOVED******REMOVED***}
***REMOVED***</script>
```

### CSS customizations

Aside from the styling of the `splash-overlay` and `splash-screen` elements, the most important part of the CSS is preventing the story from scrolling while the splash screen is active.

This is achieved using the `.no-scroll` class and setting the `overflow: hidden`.
```css
body.no-scroll {
***REMOVED***overflow: hidden; /* Prevent the story scrolling while splash screen in place */
***REMOVED***background-color: #a25d35; /* Background color while the embedded story loads */
}
```