function startAnalysis() {
    var text = document.getElementById('text-to-analyze').value;
    // ... analysis code ...
    document.getElementById('tab-buttons').classList.remove('hidden');
    document.getElementById('tabs').classList.remove('hidden');
    document.getElementById("second-input-container").classList.remove("hidden");
    showTab(0);
}

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
}
function startAnalysisfile() {
    // Get the radio button values
    var inputMethod = document.querySelector('input[name="input-method"]:checked').value;
  
    if (inputMethod === 'example') {
      // Get the text from the textarea
      var text = document.getElementById('text-to-analyze').value;
      processAnalysis(text);
    } else if (inputMethod === 'upload') {
      // Read the file content
      var fileInput = document.querySelector('input[type="file"]');
      readUploadedFile(fileInput, function(fileContent) {
        processAnalysis(fileContent);
      });
    }
  }
  
  function processAnalysis(text) {
    // ... analysis code ...
  
    document.getElementById('tab-buttons').classList.remove('hidden');
    document.getElementById('tabs').classList.remove('hidden');
    document.getElementById("second-input-container").classList.remove("hidden");
    showTab(0);
  }
  

function selectExampleData() {
    // Implement this function to handle example data selection
}



