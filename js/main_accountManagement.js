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
		
		//get transaction
		getTransaction(email);
		
		//load getSatisfiction help
		$.getScript("https://loader.engage.gsfn.us/loader.js", function(scipt){
			if (typeof GSFN !== "undefined") { GSFN.loadWidget(5632,{"containerId":"getsat-widget-5632"}); }
		});
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
			var html="<ul>", infos=["email", "accountType", "credit", "dateRegister"], v='';
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



//get transaction
function getTransaction(email){
	$("#transaction_loading").show();
	$("#transaction table").html("");
	
	$.ajax({
		url:"ws/getTransaction.py",
		data:{
			username:email
		},
		dataType:"json",
		success: function(json){
			var html='';
				theader="<tr>",
				tvalue="",
				infos=["date", "description","transaction", "balance"];
			
			//if json is array
			if(json && json instanceof Array && json.length>0){
				//from last to first
				json.reverse();
				
				$.each(json, function(i,obj){
					tvalue+='<tr>';
					$.each(infos, function(j,header){
						if(i==0){
							theader+="<td>"+header.toUpperCase()+"</td>";
						}
						tvalue+='<td>'+obj[header]+"</td>";
					});
					tvalue+='</tr>';
				});
				html+=theader+"</tr>"+tvalue;
				
				//hide loading image
				$("#transaction_loading").hide();
				
				$("#transaction table").html(html);
			}
		},
		error: function(e){
			console.log("[ERROR]getTransaction: "+ e.responseText);
		}
	});
}


//get url parameter
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}
