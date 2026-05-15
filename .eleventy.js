module.exports = function(eleventyConfig) {
  // Copy assets folder (CSS, JS, images) straight through to _site
  eleventyConfig.addPassthroughCopy("src/assets");

  // Copy root files Netlify needs
  eleventyConfig.addPassthroughCopy("src/robots.txt");
  eleventyConfig.addPassthroughCopy("src/llms.txt");

  // Watch CSS and JS so dev server auto-refreshes when they change
  eleventyConfig.addWatchTarget("src/assets/site.css");
  eleventyConfig.addWatchTarget("src/assets/site.js");

  // Filter: check if a nav item is the current page
  eleventyConfig.addFilter("isActive", function(itemUrl, pageUrl) {
    if (itemUrl === "/" && pageUrl === "/") return true;
    if (itemUrl !== "/" && pageUrl.startsWith(itemUrl)) return true;
    return false;
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_includes/layouts",
      data: "_data"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["njk", "md", "html"],
    // Match your existing URL structure: /residential.html, /pricing.html, etc.
    // (so Netlify's existing redirects keep working)
  };
};
