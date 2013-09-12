var app={
	userInfo:{
		email:null,
		accountType:null,
		credit:null,
		oauth:null
	}
}


//use json in the cookie
$.cookie.json=true;


//init
$(document).on({
	"ready": function(){
		init_ui();
	},
	"pageshow": function(){	 
		
	},
	"pageinit": function(){
		//popup not use history to avoid the problem that the dialog cannot be closed and may be redirected to other page
		$("div[data-role='popup']").popup({history:false});
	}
});



//init user interface
function init_ui(){
	var product=getURLParameter("product") || "pathgeo";
	

	//change title based on the 'product' parameter
	changeTitle(product);	
}

function emailPrompt() {
	//get email (trim off whitespace)
	$("login_msg").html("");
	var email = prompt("Enter your email address:").replace( /^\s+|\s+$/g, ''); 
	
	if (!email) {
		alert("Please enter a password!");
	} else {
		var url = 'ws/sendTempPassword.py?email=' + email;
		$.getJSON(url, function(data) {
			console.log(data);
			if (data.status != 'ok') {
				$("#login_msg").html(data.message);
			} else {
				$("#login_msg").html("Your temporary password has been sent to your email address.");
			}
		});
	}
}


//change title
function changeTitle(product){
	//change title
	var titles={
		"pathgeo":"A Geo-Targeting Social Web Analytics company <br>focusing on GIS functions, Real-time, and Impact detection.",
		"maptime":"MapTime is a web-based mapping tool that allows you to geocode<br>and geo-analyze their data (with street addresses) into maps.",
		"socialtime":"SocialTime is a real-time social media geo-search tool <br>that allows users to retrieve social media feedbacks, <br>online reputations, and customer opinions."
	}
	var title=titles[product]
	$("#mainContent h2 label").html(title)
}




//login
function login(){
	var email=$("#user_login #email").val(),
		password=$("#user_login #password").val();
	
	//loading icon
	$("#login_msg").html("<img src='images/loading.gif' width=20px />")
	
	
	if(email=="pathgeodemo"){
		success({
			status:"ok",
			msg:"login successfully",
			account:{
				oauth: null,
				credit: 2018,
				dateRegister: "2013-08-02 06:$M:11 ",
				email: "pathgeodemo",
				accountType: "free"	
			}
		});
		return;
	}
	
	
	//ajax to check if the email and password are valid
	$.ajax({
		url:"ws/login.py",
		data:{
			email:email,
			password:password
		},
		dataType:"json",
		method:"post",
		success:success,
		error: function(e){
			console.log("[ERROR] Login ajax error!!");
		}
	})
	
	
	//success
	function success(json){
		//clear error msg
			$("#login_msg").html("");

			if(json.status=='ok' && json.account){
				//write cookie
				if($("#login_cookie").is(":checked")){
					$.cookie("PathGeo", {'email': email, 'oauth': null}, { expires: 7, path: '/' });
				}
				
				callParent(json.account, 'login');
			}else{
				//show error msg
				$("#login_msg").html(json.msg);
			}
			
			//google anlytics tracking event
			_gaq.push(['_trackEvent', 'Account', 'Login', email]);
	}
	
}




//sign up 
function signup(){
	var	password=$("#user_signup #password").val(),
		confirmPassword=$("#user_signup #confirmPassword").val(),
		email=$("#user_signup #email").val();
		
	//clear msg
	$("#signup_msg").html("")
		
	//validate
	if(password=="" | confirmPassword=="" || email==""){showMsg("Please fill up all fields."); return;}
	if(password!=confirmPassword){showMsg("Password is not matched. Please check again."); return;}
	var validateEmail=/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if(validateEmail.test(email)==false){showMsg("You have entered an invalid email address! <br>Please check again"); return;}
	
	//show loading image
	$("#signup_loading").show();
	
	$.ajax({
		method:"post",
		url:"ws/signup.py", 
		data:{
			password:password,
			email:email
		},
		dataType:"json",
		success:function(json){
			//hide loading image
			$("#signup_loading").hide();
			
			if(json.status && json.status=='ok' && json.account){
				//write cookie
				$.cookie("PathGeo", {'email': email, 'oauth': null}, { expires: 7, path: '/' });
				
				callParent(json.account, 'signup');
			}else{
				showMsg(json.msg);
				return;
			}
			
			//google anlytics tracking event
			_gaq.push(['_trackEvent', 'Account', 'Sign up', email]);
		},
		error: function(e){
			console.log(e);
			
			//hide loading image
			$("#signup_loading").hide();
		}
	});
	
	
	
	//show msg
	function showMsg(msg){
		$("#signup_msg").html(msg);
	}
}




//showOauth
function showOauth(provider){
	if(parent.showOauth){
		parent.showOauth(provider);
	}else{
		console.log("[ERROR] no parent.showOauth function. Please check again.");
	}
	
}



//call parent function
function callParent(accountInfo, status){
	if(parent.writeAccountInfo){
		parent.writeAccountInfo(accountInfo, {status:status});	
	}else{
		console.log("[ERROR] no parent.writeAccountInfo function. Please check again.");
	}
	
}



//get url parameter
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))|| null;
}
