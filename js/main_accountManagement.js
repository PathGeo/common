var app={
	userInfo:{
		email:null,
		accountType:null,
		credit:null,
		oauth:null
	}
}


//init
$(document).on({
	"ready": function(){
		//get url parameter 
		var email=app.userInfo.email=getURLParameter('email'),
			oauth=app.userInfo.oauth=getURLParameter('oauth');
			
		if(oauth=='null'){oauth=null}
		
		
		//getAccount info
		getAccountInfo(email, oauth);
		
		//get transaction
		getTransaction(email, oauth);
		
		//load getSatisfiction help
		// $.getScript("https://loader.engage.gsfn.us/loader.js", function(scipt){
			// if (typeof GSFN !== "undefined") { GSFN.loadWidget(5632,{"containerId":"getsat-widget-5632"}); }
		// });
		
		//switch to the tab if any
		var tab=getURLParameter('tab');
		if(tab && tab!=""){
			$("#tab li[href='"+tab+"']").trigger('click');
		}
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
function getAccountInfo(email, oauth){
	$.ajax({
		url:"ws/queryAccount.py",
		data:{
			email:email,
			oauth:oauth
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
				
				//update account info
				callParent(app.userInfo, {"update":true});
			}
		},
		error: function(e){
			console.log("[ERROR]getAccountInfo: "+ e.responseText);
		}
	});
}



//get transaction
function getTransaction(email, oauth){
	$("#transaction_loading").show();
	$("#transaction table").html("");
	
	$.ajax({
		url:"ws/getTransaction.py",
		data:{
			email:email,
			oauth:oauth
		},
		dataType:"json",
		success: function(json){
			var html='';
				theader="<tr>",
				tvalue="",
				infos=["date", "description","transaction", "balance"];
			
			
			//if json is array
			if(json && json instanceof Array){
				//hide loading image
				$("#transaction_loading").hide();
				
				if(json.length==0){
					html="You don't have any transaction yet!";
				}else{
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
				
				}
				$("#transaction table").html(html);
				
			}
		},
		error: function(e){
			console.log("[ERROR]getTransaction: "+ e.responseText);
		}
	});
}



//change password
function changePW(){
	var oldPW=$("#oldPW").val(),
		newPW=$("#newPW").val(),
		confirmNewPW=$("#confirmNewPW").val();
	
	
	//if password is not matched
	if(newPW!=confirmNewPW){
		showMsg("The new password is not matched. Please check again."); return;
	}
	
	//show loading 
	$("#changePassword #changePassword_loading").show();
	
	//change password
	$.ajax({
		url:"ws/changePassword.py",
		data:{
			email: app.userInfo.email,
			oldPW: oldPW,
			newPW: newPW,
			oauth: app.userInfo.oauth
		},
		dataType:"json",
		success:function(json){
			//hide loading image
			$("#changePassword #changePassword_loading").hide();
			
			showMsg(json.msg);
		},
		error:function(e){
			showMsg(e.responseText);
		}
	})
	

	function showMsg(msg){
		$("#changePW_msg").html(msg);
	}
	
}






//showPayment
function showPayment(plan){
	if(plan=='plus'){
		plan=$("#sel_plus").val();
	}
	
	//redirect to accountManagement.html
	window.location.href="purchaseCredit.html?email="+app.userInfo.email+"&oauth="+app.userInfo.oauth+"&plan="+plan;
}



//get url parameter
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}


//call parent function
function callParent(accountInfo, options){
	if(parent.writeAccountInfo){
		parent.writeAccountInfo(accountInfo, options);	
	}else{
		console.log("[ERROR] no parent.writeAccountInfo function. Please check again.");
	}
	
}
