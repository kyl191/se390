

window.addEventListener('load', function() {
    var isChromium = window.chrome,
    vendorName = window.navigator.vendor;
    if(isChromium !== null && isChromium !== undefined && vendorName === "Google Inc.") {
   // is Google chrome 
    } else { 
   alert("ALERT: This web app is currently only supported on Google Chrome.")
    }
    
    var view = createView();
    initWindow(view);
    
  
    var homeButton = document.getElementById("home_button");
    homeButton.addEventListener("click",function() {
            hideBox("input_div");
            showBox("welcome_div");
    });
    
    var inputButton= document.getElementById('input_button');
        inputButton.addEventListener('click', function() {
            hideBox("welcome_div");
            showBox("input_div");
    });

    var submitButton = document.getElementById("submit_activity");
    submitButton.addEventListener("click", function(){
        
    });
});

    function initWindow(classes){
        makeWelcomeUI(classes);
        makeInputUI (classes);
        hideBox("input_div");
    }

    function makeWelcomeUI (classes) {
        var appDiv = document.getElementById('app_container');
        var welcomeView = new classes.welcomeMessageView(appDiv);
    }

    function makeInputUI(classes) {
        var appDiv = document.getElementById('app_container');
        var inputView = new classes.inputActivityOptions(appDiv);
    }

    function hideBox(elementId) {
        var div = document.getElementById(elementId);
        div.style.display = "none";
    }

    function showBox(elementId) {
        var div = document.getElementById(elementId);
        div.style.display = "block";
        if(elementId == "analysis_table" || elementId == "myCanvas"){
            div.style.display = "inline-block";
        }
    }
