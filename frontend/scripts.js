let currentArray = [];
const socket = io.connect(window.location.origin);

function showElementsInput() {
  const numElements = document.getElementById("numElements").value;
  if (numElements > 0) {
    document.getElementById("elementsInput").style.display = "block";
    document.getElementById("sortButton").style.display = "block";
  }
}

function sortArray() {
  const elementsInput = document.getElementById("elementsInput").value;
  currentArray = elementsInput.split(",").map(Number);
  visualizeArray(currentArray, "arrayContainer", "Original Array:");
}

function visualizeArray(
  array,
  containerId = "arrayContainer",
  title = "Original Array:"
) {
  console.log("Visualizing array:", array); // Debugging
  if (!Array.isArray(array)) {
    console.error("Provided array is not an array:", array); // Debugging
    return;
  }

  let container = document.getElementById(containerId);
  if (!container) {
    container = document.createElement("div");
    container.id = containerId;
    container.style.margin = "10px";
    container.style.padding = "10px";
    container.style.border = "1px solid #000";
    container.style.display = "inline-block"; // Horizontal display
    document.getElementById("visualizationContainer").appendChild(container);
  }
  container.innerHTML = `<h3>${title}</h3>`;
  const arrayContainer = document.createElement("div");
  arrayContainer.style.display = "flex";
  arrayContainer.style.flexDirection = "row";
  container.appendChild(arrayContainer);
  array.forEach((value) => {
    const bar = document.createElement("div");
    bar.classList.add("bubble");
    bar.style.height = `${value * 5}px`;
    bar.textContent = value;
    arrayContainer.appendChild(bar);
  });
}

function addMetrics(containerId, algorithm, metrics) {
  const container = document.getElementById(containerId);
  const metricsDiv = document.createElement("div");
  metricsDiv.innerHTML = `
    <p>${algorithm.charAt(0).toUpperCase() + algorithm.slice(1)} Sort:</p>
    <ul>
      <li>Comparisons: ${metrics.comparisons}</li>
      <li>Swaps: ${metrics.swaps}</li>
    </ul>
  `;
  container.appendChild(metricsDiv);
}

// Listen for array updates from the backend
socket.on("array update", (data) => {
  const { array, algorithm } = data;
  if (algorithm) {
    const containerId = `sortedArrayContainer-${algorithm}`;
    visualizeArray(array, containerId, `${algorithm} - Sorting`);
  } else {
    visualizeArray(array);
  }
});

async function runAlgorithm(algorithm, array) {
  console.log(`Running algorithm: ${algorithm}`); // Logging
  const response = await fetch("/sort", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ array, algorithm }),
  });
  const data = await response.json();
  if (!data || !Array.isArray(data.sortedArray)) {
    console.error("Invalid data received:", data); // Debugging
    return {};
  }
  const sortedArray = data.sortedArray;
  const metrics = data.metrics;
  console.log(`Algorithm: ${algorithm}, Metrics:`, metrics); // Logging
  const containerId = `sortedArrayContainer-${algorithm}`;
  visualizeArray(sortedArray, containerId, `${algorithm} Sorted Array:`);
  addMetrics(containerId, algorithm, metrics);
  return metrics;
}

async function compareAlgorithms() {
  const selectedAlgorithms = getSelectedAlgorithms();
  if (selectedAlgorithms.length === 0) {
    alert("Please select at least one sorting algorithm.");
    return;
  }
  const metricsList = [];
  for (let algorithm of selectedAlgorithms) {
    const arrayCopy = [...currentArray];
    const metrics = await runAlgorithm(algorithm, arrayCopy);
    metricsList.push({ algorithm, ...metrics });
  }
  displayMetricsComparison(metricsList);
}

document
  .getElementById("generateInputFields")
  .addEventListener("click", showElementsInput);
document.getElementById("sortButton").addEventListener("click", async () => {
  sortArray();
  const selectedAlgorithms = getSelectedAlgorithms();
  if (selectedAlgorithms.length === 0) {
    alert("Please select at least one sorting algorithm.");
    return;
  }
  for (let algorithm of selectedAlgorithms) {
    const arrayCopy = [...currentArray];
    await runAlgorithm(algorithm, arrayCopy);
  }
});
document.getElementById("compareButton").addEventListener("click", async () => {
  sortArray();
  await compareAlgorithms();
});
document.getElementById("resetButton").addEventListener("click", resetArray);
document
  .getElementById("selectAllCheckbox")
  .addEventListener("change", selectAllAlgorithms);

function resetArray() {
  // Clear the current array and input fields
  currentArray = [];
  document.getElementById("elementsInput").value = "";
  document.getElementById("elementsInput").style.display = "none";
  document.getElementById("sortButton").style.display = "none";

  // Clear all visualizations and containers
  document.getElementById("arrayContainer").innerHTML = ""; // Clear the array container
  document.getElementById("timeComplexity").innerHTML = ""; // Clear the time complexity display
  document.getElementById("chartContainer").innerHTML = ""; // Clear the chart container
  document.getElementById("visualizationContainer").innerHTML = ""; // Clear the visualization container

  // Clear metrics and sorting results
  const sortedContainers = document.querySelectorAll(
    '[id^="sortedArrayContainer-"]'
  );
  sortedContainers.forEach((container) => (container.innerHTML = "")); // Clear all sorted array containers

  // Uncheck all checkboxes (for selecting algorithms)
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((checkbox) => (checkbox.checked = false));

  // Optionally, hide or reset any additional UI elements if necessary
}

function getSelectedAlgorithms() {
  const checkboxes = document.querySelectorAll(
    'input[type="checkbox"]:checked'
  );
  const selectedAlgorithms = Array.from(checkboxes).map(
    (checkbox) => checkbox.value
  );
  console.log("Selected algorithms:", selectedAlgorithms); // Debugging
  return selectedAlgorithms;
}

function selectAllAlgorithms() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const selectAll = document.getElementById("selectAllCheckbox").checked;
  checkboxes.forEach((checkbox) => {
    checkbox.checked = selectAll;
    checkbox.dispatchEvent(new Event("change"));
  }); // Trigger change event });
}

function displayMetricsComparison(metricsList) {
  const fastest = metricsList.reduce(
    (min, m) => (m.comparisons < min.comparisons ? m : min),
    metricsList[0]
  );
  const timeComplexityDiv = document.getElementById("timeComplexity");
  timeComplexityDiv.innerHTML = "";

  metricsList.forEach((m) => {
    const color = m.algorithm === fastest.algorithm ? "limegreen" : "initial";
    timeComplexityDiv.innerHTML += `<p style="color: ${color};">${m.algorithm} - Comparisons: <strong>${m.comparisons}</strong>, Swaps: <strong>${m.swaps}</strong></p>`;
  });

  timeComplexityDiv.innerHTML += `<p><strong>Fastest Algorithm: ${fastest.algorithm}</strong> with ${fastest.comparisons} comparisons</p>`;

  displayComparisonChart(metricsList);
}

function displayComparisonChart(metricsList) {
  const chartContainer = document.getElementById("chartContainer");
  chartContainer.innerHTML = '<canvas id="comparisonChart"></canvas>';
  const ctx = document.getElementById("comparisonChart").getContext("2d");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: metricsList.map((m) => m.algorithm),
      datasets: [
        {
          label: "Comparisons",
          data: metricsList.map((m) => m.comparisons),
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
        {
          label: "Swaps",
          data: metricsList.map((m) => m.swaps),
          backgroundColor: "rgba(153, 102, 255, 0.2)",
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
