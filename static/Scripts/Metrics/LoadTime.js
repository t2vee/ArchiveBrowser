window.addEventListener('load', (event) => {
  const navigationTiming = performance.getEntriesByType('navigation')[0];
  const pageLoadTime = Math.round(navigationTiming.domComplete - navigationTiming.startTime);
  if (pageLoadTime >= 0) {

    document.getElementById("performance-metrics").innerText += ` Page: ${pageLoadTime} ms`;
  } else {
    document.getElementById("performance-metrics").innerHTML = 'Page: Timing data not available';
  }
});