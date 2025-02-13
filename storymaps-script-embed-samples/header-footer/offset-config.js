/*
  DISCLAIMER: This example code is provided for educational and demonstration purposes.
  It may not represent best practices for security and/or performance and is not intended for production use.
*/

function generateScriptConfig() {
    window.storyMapsEmbedConfig = {
      topOffset: "3rem"
    };
  }

  function createScriptedEmbed() {
    const script = document.createElement('script');
    script.id = 'embed-script';
    script.src = `https://storymapsqa.arcgis.com/embed/view`;
    script.setAttribute('data-story-id', "1ba69ca9c31b4183b1ee486c36364198");
    script.setAttribute('data-root-node', '.storymaps-root');
    document.body.appendChild(script);
  }

  generateScriptConfig();
  createScriptedEmbed();
