

function createView() {
        
	var AbstractView = function () {
    };

    _.extend(AbstractView.prototype, {
        _instantiateInterface: function (templateId, attachToElement) {
            var template = document.getElementById(templateId);
            this.hostElement = document.createElement('div');
            this.hostElement.innerHTML = template.innerHTML;
            attachToElement.appendChild(this.hostElement);
        }
    });

    var welcomeMessageView = function (attachToElement) {
	    this._instantiateInterface('welcome_message', attachToElement);
	};
    _.extend(welcomeMessageView.prototype, AbstractView.prototype);

	return {
		welcomeMessageView: welcomeMessageView,
	    
        
	};

    
}

