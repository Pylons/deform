addEvent(window, 'load', initForm);

var highlight_array = new Array();

function initForm(){
	var paymentRedirecting = checkPaypal();
	browserDetect();
	initializeFocus();
	var activeForm = document.getElementsByTagName('form')[0];
	addEvent(activeForm, 'submit', disableSubmitButton);
	ifInstructs();
	showRangeCounters();
	checkMechanicalTurk();
	if(!paymentRedirecting) initAutoResize();
}

function disableSubmitButton() {
	document.getElementById('saveForm').disabled = true;
}

// for radio and checkboxes, they have to be cleared manually, so they are added to the
// global array highlight_array so we dont have to loop through the dom every time.
function initializeFocus(){
	fields = getElementsByClassName(document, "*", "field");
	for(i = 0; i < fields.length; i++) {
		if(fields[i].type == 'radio' || fields[i].type == 'checkbox') {
			fields[i].onclick = function(){clearSafariRadios(); addClassName(this.parentNode.parentNode.parentNode, "focused", true)};
			fields[i].onfocus = function(){clearSafariRadios(); addClassName(this.parentNode.parentNode.parentNode, "focused", true)};
			highlight_array.splice(highlight_array.length,0,fields[i]);
		}
		else if(fields[i].className.match('addr')){
			fields[i].onfocus = function(){clearSafariRadios(); addClassName(this.parentNode.parentNode.parentNode, "focused", true)};
			fields[i].onblur = function(){removeClassName(this.parentNode.parentNode.parentNode, "focused")};
		}
		else if(fields[i].className.match('other')){
			fields[i].onfocus = function(){clearSafariRadios(); addClassName(this.parentNode.parentNode.parentNode, "focused", true)};
		}
		else {
			fields[i].onfocus = function(){clearSafariRadios();addClassName(this.parentNode.parentNode, "focused", true)};
			fields[i].onblur = function(){removeClassName(this.parentNode.parentNode, "focused")};
		}
	}
}

function initAutoResize() {
	var key = 'wufooForm';
	if(typeof(__EMBEDKEY) != 'undefined') key = __EMBEDKEY;
	if(parent.postMessage) {
		parent.postMessage(document.body.offsetHeight+'|'+key, "*");
	}
	else createTempCookie(key, document.body.offsetHeight);
}

function createTempCookie(name, value)
{
	var date = new Date();
	date.setTime(date.getTime()+(60*1000));
	var expires = "; expires="+date.toGMTString();
	document.cookie = name+"="+value+expires+"; domain=.wufoo.com; path=/";
	if(readTempCookie(name) != value) {
		var script = document.createElement("script");
	    script.setAttribute("src", "http://wufoo.com/forms/height.js?action=set&embedKey="+name+"&height="+value+"&timestamp = "+ new Date().getTime().toString());
	    script.setAttribute("type","text/javascript");
	    document.body.appendChild(script);
	}
}

function readTempCookie(name)
{
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++)
	{
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return '';
}

function clearSafariRadios() {
	for(var i = 0; i < highlight_array.length; i++) {
		if(highlight_array[i].parentNode) {
			removeClassName(highlight_array[i].parentNode.parentNode.parentNode, 'focused');
		}
	}
}

function ifInstructs(){
	var container = document.getElementById('public');
	if(container){
		removeClassName(container,'noI');
		var instructs = getElementsByClassName(document,"*","instruct");
		if(instructs == ''){
			addClassName(container,'noI',true);
		}
		if(container.offsetWidth <= 450){
			addClassName(container,'altInstruct',true);
		}
	}
}

function browserDetect(){
	var detect = navigator.userAgent.toLowerCase();
	var container = document.getElementsByTagName('html');
	if(detect.indexOf('firefox') + 1){
		addClassName(container[0], 'firefox', true);
	}
	else if(detect.indexOf('chrome') + 1){
		addClassName(container[0], 'chrome', true);
	}
	else if(detect.indexOf('safari') + 1){
		addClassName(container[0], 'safari', true);
	}
}

function checkPaypal() {
	var ret = false;
	if(document.getElementById('merchant')) {
		ret = true;
		if(typeof(__EMBEDKEY) == 'undefined'){
			document.getElementById('merchantMessage').innerHTML = 'Your order is being processed. Please wait a moment while we redirect you to our payment page.';
			document.getElementById('merchantButton').style.display = 'none';
		}
		document.getElementById('merchant').submit();
	}
	return ret;
}

function checkMechanicalTurk() {
	if(document.getElementById('mechanicalTurk')) {
		document.getElementById('merchantMessage').innerHTML = 'Your submission is being processed. You will be redirected shortly.';
		document.getElementById('merchantButton').style.display = 'none';
		document.getElementById('mechanicalTurk').submit();
	}
}

function showRangeCounters(){
	counters = getElementsByClassName(document, "em", "currently");
	for(i = 0; i < counters.length; i++) {
		counters[i].style.display = 'inline';
	}
}

function validateRange(ColumnId, RangeType) {
	if(document.getElementById('rangeUsedMsg'+ColumnId)) {
		var field = document.getElementById('Field'+ColumnId);
		var msg = document.getElementById('rangeUsedMsg'+ColumnId);

		switch(RangeType) {
			case 'character':
				msg.innerHTML = field.value.length;
				break;
				
			case 'word':
				var val = field.value;
				val = val.replace(/\n/g, " ");
				var words = val.split(" ");
				var used = 0;
				for(i =0; i < words.length; i++) {
					if(words[i].replace(/\s+$/,"") != "") used++;
				}
				msg.innerHTML = used;
				break;
				
			case 'digit':
				msg.innerHTML = field.value.length;
				break;
		}
	}
}

/*--------------------------------------------------------------------------*/

//http://www.robertnyman.com/2005/11/07/the-ultimate-getelementsbyclassname/
function getElementsByClassName(oElm, strTagName, strClassName){
	var arrElements = (strTagName == "*" && oElm.all)? oElm.all : oElm.getElementsByTagName(strTagName);
	var arrReturnElements = new Array();
	strClassName = strClassName.replace(/\-/g, "\\-");
	var oRegExp = new RegExp("(^|\\s)" + strClassName + "(\\s|$)");
	var oElement;
	for(var i=0; i<arrElements.length; i++){
		oElement = arrElements[i];		
		if(oRegExp.test(oElement.className)){
			arrReturnElements.push(oElement);
		}	
	}
	return (arrReturnElements)
}

//http://www.bigbold.com/snippets/posts/show/2630
function addClassName(objElement, strClass, blnMayAlreadyExist){
   if ( objElement.className ){
      var arrList = objElement.className.split(' ');
      if ( blnMayAlreadyExist ){
         var strClassUpper = strClass.toUpperCase();
         for ( var i = 0; i < arrList.length; i++ ){
            if ( arrList[i].toUpperCase() == strClassUpper ){
               arrList.splice(i, 1);
               i--;
             }
           }
      }
      arrList[arrList.length] = strClass;
      objElement.className = arrList.join(' ');
   }
   else{  
      objElement.className = strClass;
      }
}

//http://www.bigbold.com/snippets/posts/show/2630
function removeClassName(objElement, strClass){
   if ( objElement.className ){
      var arrList = objElement.className.split(' ');
      var strClassUpper = strClass.toUpperCase();
      for ( var i = 0; i < arrList.length; i++ ){
         if ( arrList[i].toUpperCase() == strClassUpper ){
            arrList.splice(i, 1);
            i--;
         }
      }
      objElement.className = arrList.join(' ');
   }
}

//http://ejohn.org/projects/flexible-javascript-events/
function addEvent( obj, type, fn ) {
  if ( obj.attachEvent ) {
    obj["e"+type+fn] = fn;
    obj[type+fn] = function() { obj["e"+type+fn]( window.event ) };
    obj.attachEvent( "on"+type, obj[type+fn] );
  } 
  else{
    obj.addEventListener( type, fn, false );	
  }
}