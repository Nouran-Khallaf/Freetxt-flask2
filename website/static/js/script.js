

function readUploadedFile(fileInput, callback) {
    var file = fileInput.files[0];
    var reader = new FileReader();
    reader.onload = function(e) {
      callback(e.target.result);
    };
    reader.onerror = function(e) {
      alert('Error reading file');
    };
    reader.readAsText(file);
  }

  function showTab(tabIndex) {
    var i;
    var tabs = document.getElementsByClassName('tab-content');
    var buttons = document.getElementsByClassName('tab-btn');
    for (i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none';
        buttons[i].classList.remove('tab-btn-selected');
    }
    document.getElementById('tab' + tabIndex).style.display = 'block';
    buttons[tabIndex].classList.add('tab-btn-selected');
}
function toggleInputOption(option) {
  
  document.getElementById('example-options').style.display = option === 'example' ? 'block' : 'none';
  document.getElementById('file-to-analyze').style.display = option === 'upload' ? 'block' : 'none';
  document.getElementById('text-input').style.display = option === 'text' ? 'block' : 'none';
  document.getElementById('tab-buttons').classList.add('hidden');
  document.getElementById('tabs').classList.add('hidden');

}

function startAnalysisfile(event) {
  event.preventDefault();

  const inputMethod = document.querySelector('input[name="input-method"]:checked').value;
  let data = new FormData();

  if (inputMethod === 'example') {
    // Handle example data
  } else if (inputMethod === 'upload') {
    const fileInput = document.querySelector('input[type="file"]');
    data.append('file', fileInput.files[0]);
    data.append('input-method', 'upload');
  } else if (inputMethod === 'text') {
    const text = document.getElementById('text-to-analyze').value;
    data.append('text-to-analyze', text);
    data.append('input-method', 'text');
    processAnalysis(text);
  
  }

  fetch('/fileanalysis', {
    method: 'POST',
    body: data
  })
  .then(response => response.json())
  .then(data => {
    if (data.sentences) {
      displaySentences(data.sentences);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
   



function processAnalysis(text) {
  // ... analysis code ...
  //console.log("Captured text:", text);
  sendTextToServer(text);
  document.getElementById('Dataview').classList.remove('hidden');  // Show the DataView div
  document.getElementById('submit-sentences-btn').classList.remove('hidden');  // Show the submit button
}
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const toggleCheckbox = document.getElementById('darkModeToggleCheckbox');

    toggleCheckbox.addEventListener('change', function() {
        if (toggleCheckbox.checked) {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
        }
    });
});

  

  

function selectExampleData() {
    // Implement this function to handle example data selection
}

function resetUI() {
  // Hide tab buttons and tabs
  document.getElementById('tab-buttons').classList.add('hidden');
  document.getElementById('tabs').classList.add('hidden');
  document.getElementById("second-input-container").classList.add("hidden");
  
  // Optionally reset other elements like the file input or text area:
  document.querySelector('input[type="file"]').value = ''; // Clear file input
  document.getElementById('text-to-analyze').value = '';   // Clear text area
}

///capture the text
function sendTextToServer(text) {
  fetch('/fileanalysis', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'text=' + encodeURIComponent(text)
  })
  .then(response => response.json())
  .then(data => {
      displaySentences(data.sentences);
  })
  .catch((error) => {
      console.error('Error:', error);
  });
}
  
  

function displaySentences(sentences) {
  const outputDiv = document.getElementById('Dataview');
  outputDiv.innerHTML = ""; // Clear previous content
  // Create a table and its parts
  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const tbody = document.createElement('tbody');

  // Create table header for checkboxes and master checkbox
  const thCheckBox = document.createElement('th');  // <-- This was the missing line
  const masterCheckbox = document.createElement('input');
  masterCheckbox.type = "checkbox";
  masterCheckbox.id = "master-check";
  masterCheckbox.checked = true;
  


  // Add the event listener right after creating the checkbox
  masterCheckbox.addEventListener("change", function() {
      const isChecked = this.checked;
      const checkboxes = document.querySelectorAll('.sentence-check');
      checkboxes.forEach(cb => {
          cb.checked = isChecked;
      });
  });

  thCheckBox.appendChild(masterCheckbox);
  thead.appendChild(thCheckBox);

  

  const thNumber = document.createElement('th');
  thNumber.innerText = "#";
  thead.appendChild(thNumber);

  const thSentence = document.createElement('th');
  thSentence.innerText = "Sentences";
  thead.appendChild(thSentence);

  table.appendChild(thead);

  sentences.forEach((sentence, index) => {
      const tr = document.createElement('tr');
      
      const tdCheckBox = document.createElement('td');
      const checkBox = document.createElement('input');
      checkBox.type = "checkbox";
      checkBox.classList.add("sentence-check");
      checkBox.value = sentence;
      checkBox.checked = true;
      tdCheckBox.appendChild(checkBox);
      tr.appendChild(tdCheckBox);

      const tdNumber = document.createElement('td');
      tdNumber.innerText = index + 1;
      tr.appendChild(tdNumber);

      const tdSentence = document.createElement('td');
      tdSentence.innerText = sentence;
      tr.appendChild(tdSentence);

      tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  outputDiv.appendChild(table);
}


function sendSelectedSentences() {
  const checkedBoxes = document.querySelectorAll('.sentence-check:checked');
  const selectedSentences = Array.from(checkedBoxes).map(cb => cb.value);
  const summaryElement = document.getElementById('summary');
  
  
  fetch("/process_sentences", {
      method: "POST",
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ sentences: selectedSentences })
  })
  .then(response => response.json())
  .then(data => {
      console.log("Full response data:", data.wordTree);
      if (data.status === "success") {
          displayWordFrequencies(data);
          displaySentimentAnalysis(data.sentimentData, data.sentimentCounts); 
          displayPlot(data.sentimentPlotPie, 'SentimentPlotViewPie');
          displayPlot(data.sentimentPlotBar, 'SentimentPlotViewBar');
          handleWordTreeData(data.wordTreeData, data.search_word);
          populateDropdown(data.wordFrequencies)
          document.getElementById('tab-buttons').classList.remove('hidden');  // Show the tab buttons
          document.getElementById('tabs').classList.remove('hidden');  // Show the tabs content
          showTab(0);  // Automatically switch to the analysis tab
           // Display the summary in the appropriate location
  
          summaryElement.textContent = data.summary;
          document.getElementById('scattertextIframe').src = data.scatterTextHtml;

        
      } else {
          console.error("Error processing sentences:", data);
      }
  })
  .catch(error => {
      console.error("Error sending selected sentences:", error);
  });
}




function displayWordFrequencies(data) {
  const outputDiv = document.getElementById('Freqview');
  outputDiv.innerHTML = ""; // Clear previous content

  // Check if there are word frequencies to display
  if (!data.wordFrequencies) {
      outputDiv.innerText = "No word frequencies to display.";
      return;
  }

  // Create a table
  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const tbody = document.createElement('tbody');

  // Add table headers
  const thWord = document.createElement('th');
  thWord.innerText = "Word";
  thead.appendChild(thWord);

  const thFrequency = document.createElement('th');
  thFrequency.innerText = "Frequency";
  thead.appendChild(thFrequency);

  table.appendChild(thead);

  // Populate table with word frequencies
  for (let word in data.wordFrequencies) {
      const tr = document.createElement('tr');
      
      const tdWord = document.createElement('td');
      tdWord.innerText = word;
      tr.appendChild(tdWord);

      const tdFrequency = document.createElement('td');
      tdFrequency.innerText = data.wordFrequencies[word];
      tr.appendChild(tdFrequency);

      tbody.appendChild(tr);
  }

  table.appendChild(tbody);
  outputDiv.appendChild(table);

}
let currentPagesent = 1;
const itemsPerPagesent = 10; // or whatever number you choose
let totalPagessent = 1; // This will be calculated based on data length

function displaySentimentAnalysis(sentimentData, sentimentCounts) {
    const outputDiv = document.getElementById('SentimentView');
    outputDiv.innerHTML = ""; // Clear previous content
    
    totalPagessent = Math.ceil(sentimentData.length / itemsPerPagesent);
    const currentData = sentimentData.slice((currentPagesent-1)*itemsPerPagesent, currentPagesent*itemsPerPagesent);
    
    // Check if there is sentiment data to display
  if (!sentimentData) {
    outputDiv.innerText = "No sentiment analysis results to display.";
    return;
}

// Create a table for sentiment data
const tableData = document.createElement('table');
const theadData = document.createElement('thead');
const tbodyData = document.createElement('tbody');

tableData.id = "data-table";
tableData.className = "w3-table w3-bordered w3-striped w3-hoverable w3-small";
// Add table headers for sentiment data
const headers = ["Review", "Sentiment Label", "Sentiment Score"];
headers.forEach(header => {
    const th = document.createElement('th');
    th.innerText = header;
    theadData.appendChild(th);
});

tableData.appendChild(theadData);

// Populate table with sentiment analysis results
// Populate table with sentiment analysis results
currentData.forEach(row => {  // Change sentimentData to currentData
    const tr = document.createElement('tr');

    const tdReview = document.createElement('td');
    tdReview.innerText = row.Review;
    tr.appendChild(tdReview);

    const tdLabel = document.createElement('td');
    tdLabel.innerText = row['Sentiment Label'];
    tr.appendChild(tdLabel);

    const tdScore = document.createElement('td');
    tdScore.innerText = row['Sentiment Score'];
    tr.appendChild(tdScore);

    tbodyData.appendChild(tr);
});


tableData.appendChild(tbodyData);
outputDiv.appendChild(tableData);

// Handle sentiment counts
const countsHeader = document.createElement('h3');
countsHeader.innerText = "Sentiment Counts";
outputDiv.appendChild(countsHeader);

const ulCounts = document.createElement('ul');
for (let sentiment in sentimentCounts) {
  const li = document.createElement('li');
  li.innerText = `${sentiment}: ${sentimentCounts[sentiment]}`;
  ulCounts.appendChild(li);
}

    outputDiv.appendChild(ulCounts);
    
    createPaginationControlsent(outputDiv, sentimentData);
}

function createPaginationControlsent(container, data) {
    const navElement = document.createElement('div');
    navElement.className = 'w3-center w3-padding-16';
    
    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'w3-bar';

    if (currentPagesent > 1) {
        const prevButton = document.createElement('a');
        prevButton.className = 'w3-button w3-hover-black';
        prevButton.innerText = '« Previous';
        prevButton.addEventListener('click', function() {
            currentPagesent--;
            displaySentimentAnalysis(data, null); // passing null as sentimentCounts because this example assumes you're only paginating sentimentData. Modify as needed.
        });
        paginationDiv.appendChild(prevButton);
    }

    const pageInfo = document.createElement('span');
    pageInfo.className = 'w3-bar-item w3-border w3-padding';
    pageInfo.innerText = `Page ${currentPagesent} of ${totalPagessent}`;
    paginationDiv.appendChild(pageInfo);

    if (currentPagesent < totalPagessent) {
        const nextButton = document.createElement('a');
        nextButton.className = 'w3-button w3-hover-black';
        nextButton.innerText = 'Next »';
        nextButton.addEventListener('click', function() {
            currentPagesent++;
            displaySentimentAnalysis(data, null); 
        });
        paginationDiv.appendChild(nextButton);
    }

    navElement.appendChild(paginationDiv);
    container.appendChild(navElement);
}




function displayPlot(plotHtml, elementId) {
  const plotContainer = document.getElementById(elementId);
  if (plotContainer) {
      plotContainer.innerHTML = plotHtml;

      // Find and execute scripts if any
      Array.from(plotContainer.getElementsByTagName("script")).forEach(oldScript => {
          const newScript = document.createElement("script");
          Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
          newScript.appendChild(document.createTextNode(oldScript.innerHTML));
          oldScript.parentNode.replaceChild(newScript, oldScript);
      });
  } else {
      console.error("Cannot find the", elementId, "element");
  }
}

function displayWordTree(wordTreeHtml) {
  const wordTreeContainer = document.getElementById('wordTreeContainer');
  wordTreeContainer.innerHTML = wordTreeHtml;

  // For dynamic script execution:
  Array.from(wordTreeContainer.getElementsByTagName("script")).forEach(oldScript => {
      const newScript = document.createElement("script");
      Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}

let currentWordTreeData;  // Global variables
let currentSearchWord;
//  get the WordTree data from Flask
function handleWordTreeData(wordTreeData, search_word) {
    currentWordTreeData = wordTreeData;  // Store data in global variable
    currentSearchWord = search_word;     // Store search word in global variable
    
    google.charts.load('current', { packages: ['wordtree'] });
    google.charts.setOnLoadCallback(function () {
        drawWordTree(currentWordTreeData, currentSearchWord);
    });
    
    // Move your event listener setup here so it's only set up once you've got data:
    window.addEventListener('resize', () => {
        drawWordTree(currentWordTreeData, currentSearchWord);
    });
}

function drawWordTree(wordTreeData, search_word) {
    const container = document.getElementById('wordtree_basic');
  
    // Set explicit dimensions if needed
    container.style.width = window.innerWidth + 'px';
    container.style.height = window.innerHeight + 'px';
  
    const data = google.visualization.arrayToDataTable(wordTreeData);
    const options = {
        wordtree: {
            format: 'implicit',
            type: 'double',
            word: 'castle',
            colors: ['red', 'black', 'green']
        }
    };
  
    const chart = new google.visualization.WordTree(container);
    chart.draw(data, options);
  }
  



  
function startAnalysisfile_uploaded(event) {
  event.preventDefault(); // To prevent the form from submitting in the traditional way
  
  const formData = new FormData(document.getElementById("text-analysis-form"));
  
  fetch("/fileanalysis", {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if (data.columns) {
          populateColumns(data.columns);
      }
  })
  .catch(error => console.error('Error:', error));
}

function populateColumns(columns) {
  document.getElementById('column-selection').classList.remove('hidden'); 
  const dropdownElement = document.getElementById('columns-dropdown');
  
  // Reset dropdown
  dropdownElement.innerHTML = '';
  
  // Populate options
  columns.forEach(column => {
      const option = document.createElement('option');
      option.value = column;
      option.innerText = column;
      dropdownElement.appendChild(option);
  });

  // Initialize Choices.js

  const choices = new Choices(dropdownElement, {
  removeItemButton: true, // To allow removal of selected items
  allowHTML: false, // Explicitly set to false if you don't need HTML content
});
}


function viewSelectedColumns(event) {
  //document.getElementById('Dataview').classList.add('hidden'); 
  document.getElementById('submit-rows-btn').classList.remove('hidden');
  if (event) event.preventDefault();
  // Get selected columns from the dropdown
  const dropdown = document.getElementById('columns-dropdown');
  const selectedColumns = [...dropdown.options]
      .filter(option => option.selected)
      .map(option => option.value);

  if (selectedColumns.length === 0) {
      alert("No columns selected!");
      return;
  }

  // Send selected columns to the Flask server
  fetch('/fileanalysis', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          input_method: 'columns',
          selectedColumns: selectedColumns
      })
  })
  .then(response => response.json())
  .then(data => {
      // Handle the response from the server
      if (data.message && data.message === "Data extracted") {
          initializeAllRowsAsSelected(data.data);
          displayDatatable(data.data);
      } else {
          console.error("Error fetching data:", data);
      }
  })
  .catch(error => {
      console.error("Error:", error);
  });
}

let currentPage = 1;
const itemsPerPage = 15;
let totalPages;
let allSelectedRows = [];
let allData = [];
let displayData = [];
function initializeAllRowsAsSelected(data) {
    allSelectedRows = data.map(row => JSON.stringify(row));
}

function displayDatatable(data) {
    const dataToDisplay = displayData.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
    const tableContainer = document.getElementById('data-table-container');
    tableContainer.innerHTML = "";  // Clear previous table data

    totalPages = Math.ceil(data.length / itemsPerPage);

    // Create a table
    const table = document.createElement('table');
    table.id = "data-table";
    table.className = "w3-table w3-bordered w3-striped";
    // Table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    // Checkbox header with master checkbox
    const thCheckBox = document.createElement('th');
    const masterCheckbox = document.createElement('input');
    masterCheckbox.type = "checkbox";
    masterCheckbox.id = "master-check";
    masterCheckbox.checked = true;
    masterCheckbox.addEventListener("change", function() {
        const isChecked = this.checked;
        const checkboxes = document.querySelectorAll('.data-row-check');
        checkboxes.forEach((cb, index) => {
            cb.checked = isChecked;

            const currentIndex = (currentPage - 1) * itemsPerPage + index;
            const rowString = JSON.stringify(data[currentIndex]);
            if (isChecked && !allSelectedRows.includes(rowString)) {
                allSelectedRows.push(rowString);
            } else {
                const rowIndex = allSelectedRows.indexOf(rowString);
                if (rowIndex !== -1) {
                    allSelectedRows.splice(rowIndex, 1);
                }
            }
        });
    });
    thCheckBox.appendChild(masterCheckbox);
    headerRow.appendChild(thCheckBox);

// Create headers from data keys
Object.keys(data[0]).forEach(key => {
    const th = document.createElement('th');

    // Add column title
    const title = document.createElement('div');
    title.textContent = key;
    th.appendChild(title);

    // Create the dropdown for filtering
    const dropdown = document.createElement('select');
    dropdown.className = 'w3-select';
    dropdown.id = `filter-${key}`;
    dropdown.onchange = function() {
        filterByColumn(data, key, this.value);
    };

    const uniqueValues = [...new Set(data.map(item => item[key]))];
    dropdown.add(new Option('All', ''));
    uniqueValues.forEach(value => {
        dropdown.add(new Option(value, value));
    });

    th.appendChild(dropdown);
    headerRow.appendChild(th);
});

    thead.appendChild(headerRow);  // Append headerRow to thead
    table.appendChild(thead);      // Append thead to table
    // Table body
    const tbody = document.createElement('tbody');
    for (let i = (currentPage - 1) * itemsPerPage; i < currentPage * itemsPerPage && i < data.length; i++) {
        const tr = document.createElement('tr');

        const tdCheckBox = document.createElement('td');
        const checkBox = document.createElement('input');
        checkBox.type = "checkbox";
        checkBox.classList.add("data-row-check");
        checkBox.value = JSON.stringify(data[i]);
        checkBox.checked = true;  // Initialize checkboxes in the checked state

        // Event listener for individual checkboxes
        checkBox.addEventListener("change", function() {
            const rowString = this.value;
            if (this.checked && !allSelectedRows.includes(rowString)) {
                allSelectedRows.push(rowString);
            } else {
                const index = allSelectedRows.indexOf(rowString);
                if (index !== -1) {
                    allSelectedRows.splice(index, 1);
                }
            }
        });

        tdCheckBox.appendChild(checkBox);
        tr.appendChild(tdCheckBox);

        // Data from the row
        Object.values(data[i]).forEach(value => {
            const td = document.createElement('td');
            td.innerText = value;
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    }

    table.appendChild(tbody);
    tableContainer.appendChild(table);

    createPaginationControls(tableContainer, data);
}

function createPaginationControls(container, data) {
    const navElement = document.createElement('nav');
    navElement.setAttribute('aria-label', "Page navigation");
    
    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'pagination-controls';

    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.innerText = 'Previous';
        prevButton.addEventListener('click', function() {
            currentPage--;
            displayDatatable(data);
        });
        paginationDiv.appendChild(prevButton);
    }

    const pageInfo = document.createElement('span');
    pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;
    paginationDiv.appendChild(pageInfo);

    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.innerText = 'Next';
        nextButton.addEventListener('click', function() {
            currentPage++;
            displayDatatable(data);
        });
        paginationDiv.appendChild(nextButton);
    }

    navElement.appendChild(paginationDiv);
    container.appendChild(navElement);
}
let filterState = {};

function filterByColumn(data, column, value) {
    filterState[column] = value; // Update the filter state

    const rows = document.getElementById('data-table').getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        let shouldShowRow = true;
        for (const filterColumn in filterState) {
            const filterValue = filterState[filterColumn];
            const cellValue = rows[i].cells[Object.keys(data[0]).indexOf(filterColumn) + 1].innerText;
            if (filterValue !== '' && cellValue !== filterValue) {
                shouldShowRow = false;
                break;  // Exit loop if this row shouldn't be displayed
            }
        }
        rows[i].style.display = shouldShowRow ? "" : "none";
    }
}




// After you fetch your data
// initializeAllRowsAsSelected(data);
// displayDatatable(data);



//document.addEventListener('DOMContentLoaded', (event) => {
  //document.getElementById('file').addEventListener('change', function() {
  
 
  // Send an AJAX request to clear the session
  //fetch('/clear-session', {
    //  method: 'POST'
  //})
  //.then(response => response.json())
  //.then(data => {
  //    console.log(data.message);
  //})
  //.catch(error => {
   //   console.error("Error:", error);
 //// });
//});
//});
function resetColumnSelection() {
  // Hide the main container
  document.getElementById('column-selection').style.display = 'none';

  // Clear the dropdown
  document.getElementById('columns-dropdown').innerHTML = '';

  // Clear the data table container
  document.getElementById('data-table-container').innerHTML = '';

  // Reset visibility of other inner elements
  document.getElementById('columns-container').classList.add('hidden');
}

function sendSelectedRows() {
  console.log("Function sendSelectedRows triggered");
  // Show loading element
  const loadingElement = document.getElementById('loading');
  loadingElement.style.display = 'flex';
  
  // Process all selected rows from allSelectedRows array
  const mergedData = allSelectedRows.map(rowString => {
      const row = JSON.parse(rowString);
      return Object.values(row).join(' ');  // Merge all string columns into one string
  });

  console.log(mergedData);

  // Send the mergedData to the server for processing
  fetch("/process_rows", {
      method: "POST",
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ mergedData: mergedData })
  })
  .then(response => response.json())
  .then(data => {
      console.log("Full response data:", data.wordTree);

      if (data.status === "success") {
          loadingElement.style.display = 'none';
          // Handle the response data 
          displayWordFrequencies(data);
          displaySentimentAnalysis(data.sentimentData, data.sentimentCounts);
          displayPlot(data.sentimentPlotPie, 'SentimentPlotViewPie');
          displayPlot(data.sentimentPlotBar, 'SentimentPlotViewBar');
          handleWordTreeData(data.wordTreeData, currentSearchWord);
          populateDropdown(data.wordFrequencies)
          document.getElementById('tab-buttons').classList.remove('hidden');  // Show the tab buttons
          document.getElementById('tabs').classList.remove('hidden');  // Show the tabs content
          showTab(0);  // Automatically switch to the analysis tab

          const summaryElement = document.getElementById('summary');
          summaryElement.textContent = data.summary;

          const iframeElem = document.getElementById('scattertextIframe');
          sendWordCloudRequest();
          iframeElem.style.opacity = 0.99;
          requestAnimationFrame(() => {
              iframeElem.src = data.scatterTextHtml + "?t=" + new Date().getTime();
          });
          document.getElementById('scattertextIframe').style.display = 'none';
          setTimeout(() => {
              document.getElementById('scattertextIframe').style.display = 'block';
          }, 50);
          iframeElem.contentWindow.location.reload(true);
      } else {
          loadingElement.style.display = 'none';
          console.error("Error processing rows:", data);
      }
  })
  .catch(error => {
      loadingElement.style.display = 'none';
      console.error("Error sending selected rows:", error);
  });
}

function reloadIframe() {
  const iframe = document.getElementById('scattertextIframe');
  //iframe.src = iframe.src;
  iframe.contentWindow.location.reload(true);
}

function sendWordCloudRequest() {
    const cloudTypeDropdown = document.querySelector('select[name="cloud_type"]');
    const selectedCloudType = cloudTypeDropdown.value;
    const cloudshapeDropdown = document.querySelector('select[name="cloud_shape"]');
    const selectedCloudshape = cloudshapeDropdown.value;
    const cloudcolorDropdown = document.querySelector('select[name="cloud_outline_color"]');
    const selectedCloudcolor = cloudcolorDropdown.value;

    const wordCloudImageElement = document.getElementById('wordCloudImage');
    
    fetch("/generate_wordcloud", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cloud_type: selectedCloudType,
            cloud_shape: selectedCloudshape,
            cloud_outline_color: selectedCloudcolor
        })
    })
    .then(response => response.json())
    .then(data => {
        
        wordCloudImageElement.src = data.wordcloud_image_path;
        wordCloudImageElement.style.display = 'block';  // Display the image

        // Handle word list and generate checkboxes
        const wordListContainer = document.getElementById('wordListContainer');
        wordListContainer.innerHTML = '';  // Clear any previous checkboxes

        // Create 'Select/Deselect All' checkbox
        const selectAllContainer = document.createElement('div');
        const selectAllLabel = document.createElement('label');
        const selectAllCheckbox = document.createElement('input');
        selectAllCheckbox.type = 'checkbox';
        selectAllCheckbox.onclick = function() {
        toggleCheckboxes(this.checked);
        };
    selectAllLabel.appendChild(selectAllCheckbox);
    selectAllLabel.appendChild(document.createTextNode(" Select/Deselect All"));
    selectAllContainer.appendChild(selectAllLabel);
    wordListContainer.appendChild(selectAllContainer);

    // Generate checkboxes for words
    data.word_list.forEach(word => {
    
    const wordContainer = document.createElement('div');
    const label = document.createElement('label');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = word;
    checkbox.checked = true;
    checkbox.className = 'word-checkbox';  
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(` ${word}`));
    wordContainer.appendChild(label);
    wordListContainer.appendChild(wordContainer);
    });
    })
    .catch(error => {
        console.error("Error generating word cloud:", error);
    });
}

function toggleCheckboxes(isChecked) {
    document.querySelectorAll('.word-checkbox').forEach(checkbox => {
        checkbox.checked = isChecked;
    });
}
document.addEventListener("DOMContentLoaded", function() {
    const cloudTypeDropdown = document.querySelector('[name="cloud_type"]');
    const cloudShapeDropdown = document.querySelector('[name="cloud_shape"]');
    const cloudOutlineColorDropdown = document.querySelector('[name="cloud_outline_color"]');

    cloudTypeDropdown.addEventListener('change', generateWordClouds);
    cloudShapeDropdown.addEventListener('change', generateWordClouds);
    cloudOutlineColorDropdown.addEventListener('change', generateWordClouds);
});


function generateWordClouds() {
    const loadingElement = document.getElementById('loading');
    loadingElement.style.display = 'flex';
    const formData = new FormData(document.getElementById('wordCloudForm'));
    const data = {
        cloud_type: formData.get('cloud_type'),
        cloud_shape: formData.get('cloud_shape'),
        cloud_outline_color: formData.get('cloud_outline_color')
    };
    console.log(data);
    fetch('/generate_wordcloud', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            
            
            const wordCloudImageElement = document.getElementById('wordCloudImage');
            wordCloudImageElement.src = "";
            wordCloudImageElement.style.display = 'none';

            setTimeout(() => {
                // Set the new wordcloud image and checkboxes after the delay
                wordCloudImageElement.src = data.wordcloud_image_path;
                wordCloudImageElement.style.display = 'block';
                renderWordCheckboxes(data.word_list);
                loadingElement.style.display = 'none';
            }, 5000)
            
            renderWordCheckboxes(data.word_list);
        }
    })
    .catch(error => {
        console.error("Error generating word cloud:", error);
    });
}
function renderWordCheckboxes(wordList) {
    const wordListContainer = document.getElementById('wordListContainer');
    wordListContainer.innerHTML = '';  // Clear previous word checkboxes

    // Generate checkboxes for words
    wordList.forEach(word => {
        const wordContainer = document.createElement('div');
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = word;
        checkbox.className = 'word-checkbox';  // For the select/deselect function

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` ${word}`));
        wordContainer.appendChild(label);
        wordListContainer.appendChild(wordContainer);
    });
}


$(document).ready(function() {

    // Range summarization script
    $('#chosen_ratio').on('input change', function() {
        $('#ratio-value').text($(this).val() + "%");

        var textInput = $('#text-to-analyze').val();
        
        $.ajax({
            type: 'POST',
            url: '/summarise',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ 
                'chosen_ratio': $(this).val(),
                'sentences': textInput
            }),
            success: function(data) {
                $('#summary').html(data.summary);
            },
            // Optionally, you can add an error handling function here
            error: function(jqXHR, textStatus, errorThrown) {
                // Handle the error
                console.error("Request failed: ", textStatus);
            }
        });
    });

    // Tabs control script
    $(".tab-btn").click(function(){
        var index = $(".tab-btn").index(this);
        $(".tab-btn").removeClass('active');
        $(this).addClass('active');
        $(".tab-content").hide();
        $("#tab" + index).show();
    });
  
    $(".tab-btn").first().trigger('click');

    // Dark mode script
    if (localStorage.getItem('dark-mode') === 'enabled') {
        $('#darkModeToggle').prop('checked', true);
        $('body').addClass('dark-mode').removeClass('light-mode');
    }

    $('#darkModeToggle').on('change', function() {
        if ($(this).is(':checked')) {
            localStorage.setItem('dark-mode', 'enabled');
            $('body').addClass('dark-mode').removeClass('light-mode');
        } else {
            localStorage.setItem('dark-mode', 'disabled');
            $('body').removeClass('dark-mode').addClass('light-mode');
        }
    });
});


function populateDropdown(wordFrequencies) {
    const dropdown = document.getElementById("wordDropdown");

    // Convert the wordFrequencies object to an array of [word, frequency] pairs
    const wordFrequencyPairs = Object.entries(wordFrequencies);

    // Sort the array by the frequency in descending order
    wordFrequencyPairs.sort((a, b) => b[1] - a[1]);

    // Iterate over the sorted wordFrequencyPairs to populate the dropdown
    for (let [word, frequency] of wordFrequencyPairs) {
        const option = document.createElement("option");
        option.value = word;
        option.text = `${word} (${frequency})`;
        dropdown.add(option);
    }
}


$(document).ready(function() {

    // Event when the dropdown selection changes
    $("#wordDropdown").change(function() {
        // Get the currently selected word from the dropdown
        const selectedWord = $(this).val();
        $("#kwicTable").removeClass("hidden");
        $("#collocsTable").removeClass("hidden");
        // Check if the word is not empty (to avoid unnecessary requests)
        if (selectedWord) {
            // Make the AJAX request
            $.post('/Keyword_collocation', { word_selection: selectedWord }, function(data) {
                if (data.kwic_results) {
                    displayKWICResults(data.kwic_results);
                }

                if (data.collocs) {
                    displayCollocs(data.collocs);
                }
                $("#graphContainer").html(`<iframe src="${data.graph_path}" width="100%" height="750px"></iframe>`);
            });
        }
    });

});

function displayKWICResults(kwicResults) {
    const kwicTable = $("#kwicTable").DataTable({
        destroy: true, // This ensures that if the DataTable is reinitialized, the previous instance is destroyed
        columns: [
            {
                className: "left-context",
                render: function(data) {
                    return '<div class="text-right">' + data + '</div>';
                }
            },
            {
                className: "keyword",
                render: function(data) {
                    return '<div class="text-center bg-primary text-white rounded p-1">' + data + '</div>';
                }
            },
            {
                className: "right-context",
                render: function(data) {
                    return '<div class="text-left">' + data + '</div>';
                }
            }
        ]
    });

    kwicTable.clear(); // Clear previous data

    kwicResults.forEach(item => {
        kwicTable.row.add([item[0], item[1], item[2]]);
    });

    kwicTable.draw();
}







function displayCollocs(collocs) {
    const collocsTable = $("#collocsTable").DataTable(); // Initialize DataTables
    collocsTable.clear(); // Clear previous data

    collocs.forEach(item => {
        collocsTable.row.add([item[0], item[1]]);
    });

    collocsTable.draw();
}

