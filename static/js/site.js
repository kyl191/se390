

window.addEventListener('load', function() {
    var isChromium = window.chrome,
    vendorName = window.navigator.vendor;
    
    var view = createView();
    initWindow(view);
    
    var submitButton = document.getElementById("submit_activity");
    submitButton.addEventListener("click", function(){
        var link = 'webcal://0.0.0.0:5000/api/schedule';
        var faculty = document.getElementById("faculty").value;
        var level = document.getElementById("level_dropdown").value;

        if(faculty && level){
            link+= '?faculty=' + faculty;
            link+='&level=' + level;
            link+='&status=co-op';
        }
        else if(faculty){
            link+= '?faculty=' + faculty;
            link+='&status=co-op';
        }
        else if(level){
            link+='?level=' + level;
            link+='&status=co-op';
        }

        window.location.href = link;
    });
});


    function initWindow(classes){
        makeWelcomeUI(classes);
    }

    function makeWelcomeUI (classes) {
        var appDiv = document.getElementById('app_container');
        var welcomeView = new classes.welcomeMessageView(appDiv);
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
