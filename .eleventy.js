module.exports = function(eleventyConfig) {
  // Copy assets folder (CSS, JS, images) straight through to _site
  eleventyConfig.addPassthroughCopy("src/assets");

  // Copy root files Netlify needs
  eleventyConfig.addPassthroughCopy("src/robots.txt");
  eleventyConfig.addPassthroughCopy("src/llms.txt");

  // Watch CSS and JS so dev server auto-refreshes when they change
  eleventyConfig.addWatchTarget("src/assets/site.css");
  eleventyConfig.addWatchTarget("src/assets/site.js");


  // Minify HTML on production builds (Netlify), skip in local dev for speed
  if (process.env.NODE_ENV === "production" || process.env.ELEVENTY_ENV === "production") {
    const htmlmin = require("html-minifier-terser");
    eleventyConfig.addTransform("htmlmin", async function(content) {
      if (this.page && this.page.outputPath && this.page.outputPath.endsWith(".html")) {
        return await htmlmin.minify(content, {
          collapseWhitespace: true,
          removeComments: true,
          minifyCSS: true,
          minifyJS: true,
          removeRedundantAttributes: true,
          removeScriptTypeAttributes: true,
          removeStyleLinkTypeAttributes: true,
          useShortDoctype: true,
          sortAttributes: true,
          sortClassName: true
        });
      }
      return content;
    });
  }

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
