var app={
	userInfo:{
		email:null,
		accountType:null,
		credit:null
	}
}


//init
$(document).on({
	"ready": function(){
		//get url parameter 
		var email=app.userInfo.email=getURLParameter('email')
		
		//getAccount info
		getAccountInfo(email);
	},
	"pageshow": function(){	 
		init_ui();
	},
	"pageinit": function(){
		//popup not use history to avoid the problem that the dialog cannot be closed and may be redirected to other page
		$("div[data-role='popup']").popup({history:false});
	}
});



//init user interface
function init_ui(){
	//click event on tab
	$("#tab li").click(function(){
		var $this=$(this);
		
		//hide all content
		$(".content").hide();
		
		//show content
		$("#"+$this.attr('href')).show();
	})
	
	
	
	
}



//get account info
function getAccountInfo(email){
	$.ajax({
		url:"ws/queryAccount.py",
		data:{
			email:email
		},
		dataType:"json",
		success: function(json){
			var html="<ul>", infos=["email", "accountType", "credit", "dataRegister"], v='';
			if(json && json.account){
				$.each(infos, function(i,k){
					if(json.account[k]){
						v=json.account[k];
						html+="<li><label>"+k.replace("_", " ").toUpperCase()+"</label>: "+ v +"</li>";
						
						if(k in app.userInfo){app.userInfo[k]=v}
					}
				})
				html+="</ul>";
				$("#accountDetail").html(html);
			}
		},
		error: function(e){
			console.log("[ERROR]getAccountInfo: "+ e.responseText);
		}
	});
}




//get url parameter
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}
