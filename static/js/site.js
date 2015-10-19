

window.addEventListener('load', function() {
    
    var view = createView();
    initWindow(view);
    
    var submitButton = document.getElementById("submit_activity");
    submitButton.addEventListener("click", function(){
        var link = window.location.href;
        link = link.replace('http', 'webcal');
        link+= "api/schedule";
        var faculty = '';
        var level = '';
        faculty = document.getElementById("faculty").value;
        level = document.getElementById("level_dropdown").value;
        if(faculty!= '' && level!= ''){
            console.log("hi");
            link+= '?faculty=' + faculty;
            link+='&level=' + level;
            link+='&status=co-op';
        }
        else if(faculty!=''){
            console.log('hi');
            link+= '?faculty=' + faculty;
            link+='&status=co-op';
        }
        else if(level!=''){
            console.log('hi');
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
