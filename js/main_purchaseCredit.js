var app={
	userInfo:{
		email:null,
		plan:null,
		oauth:null
	}
}


//init
$(document).on({
	"pageshow": function(){	 
		init();
	},
	"pageinit": function(){
		//popup not use history to avoid the problem that the dialog cannot be closed and may be redirected to other page
		$("div[data-role='popup']").popup({history:false});
	}
});



//init user interface
function init(){	
	//get url parameter 
	var email=app.userInfo.email=getURLParameter('email'),
		plan=app.userInfo.plan=getURLParameter('plan');
		oauth=app.userInfo.oauth=getURLParameter('oauth');
	
	if(oauth=='null'){oauth=app.userInfo.oauth=null}
	
	showPayment(plan);
	
	//validate credit card number
	$("#payment_cardNumber").validateCreditCard(validateCreditCard);
}



//validate credit card number
function validateCreditCard(result){
	//if creditCard number does not input anything
	var $number=$('#payment_cardNumber');
	if($number.val()==''){
		//image change back to color one
		$('.creditCardImage').each(function(){
			$(this).attr('src', $(this).attr('src_color'));
		})
		$("#payment_msg").html('');
		return;
	}
	
	app.userInfo.valideCreditcard=false;
	
	if(result.card_type!=null){
		var name=result.card_type.name;
		
		//change credit card image to bw
		$(".creditCardImage").each(function(){
			var src_bw=$(this).attr('src_bw');
			$(this).attr('src', src_bw);
		})
		
		var id="",src='',filename='', $obj=null;
		switch(name){
			case "visa":
			case "visa_electron":
				id="creditCardImage_visa";
			break;
			case "amex":
				id='creditCardImage_amex'
			break;
			case "mastercard":
				id='creditCardImage_master'
			break;		
		}
		
		$obj=$("#"+id);
		src=$obj.attr("src")
		filename=src.split("_bw.gif")[0]+".gif";
		$obj.attr("src", filename);
	}
	
	//validate credit card length
	if(!result.luhn_valid){
		showPaymentMsg("Please input the correct credit card number.");	
		return;
	}else{
		$("#payment_msg").html('');
		app.userInfo.valideCreditcard=true;
	}
}


//show payment
function showPayment(plan){	
	var price, credit;
	
	switch(plan){
		case "plusA":
			price=10;
			credit=3000;
		break;
		case "plusB":
			price=50;
			credit=5000;
		break;
		case "pro":
			price=99;
			credit="Unlimited";
		break;
	}
	//set up payment amount infcrmation
	$("#payment_amount").html("$"+price+" USD");
	$("#payment_credit").html(credit+" Credits");
	$("#payment_button").attr("name", plan)
			

	//google anlytics tracking event
	if(price==99){
		_gaq.push(['_trackEvent', 'Account', 'Pro', app.userInfo.email]);
	}else{
		if(price>0 && price<99){
			_gaq.push(['_trackEvent', 'Account', 'Plus', app.userInfo.email]);
		}
	}
}



//purchase
function purchase(){
	//validate	
	var plan=app.userInfo.plan || null,
		card_name=$("#payment_cardName").val() || null,
		card_number=$("#payment_cardNumber").val() || null,
		card_expiryMonth=$("#payment_expiryDate_month").val() || null,
		card_expiryYear=$("#payment_expiryDate_year").val() || null,
		card_authNumber=$("#payment_authNumber").val() || null,
		expiryDate='';
		
		
	if(plan && card_name && card_number && card_expiryMonth && card_expiryYear && card_authNumber){
		//if cardNumber or expiryMonth is not a number
		if(isNaN(card_number) || isNaN(card_expiryMonth) || isNaN(card_expiryYear) || isNaN(card_authNumber)){
			showPaymentMsg('Card Number, expiry Date, or Security code is not a number. Please check and input a valid number.');
			return ;
		}else{
			//check expiry date
			if(card_expiryYear.length==2){
				showPaymentMsg('Expiry year should be 4 digits, such as 2013. Please check again');
				$('#payment_expiryDate_year').focus();
				return; 
			}
			
			var year=parseInt(card_expiryYear), month=parseInt(card_expiryMonth), nowYear=new Date().getFullYear();
			if(year<nowYear || year >=2100){
				showPaymentMsg('Expiry Date is not correct. Please check again.');
				$('#payment_expiryDate_year').focus();
				return; 
			}
			if(month<=0 || month>=13){
				showPaymentMsg('Expiry Date is not correct. Please check again.');
				$('#payment_expiryDate_month').focus();
				return; 
			}
			
			card_expiryYear=card_expiryYear.substr(card_expiryYear.length-2);
			
			//if only one digit for the month, add 0 to the month
			if(card_expiryMonth.length==1){card_expiryMonth="0"+card_expiryMonth}
			expiryDate=card_expiryMonth+card_expiryYear;
			
			
			if(app.userInfo.valideCreditcard){
				//show loading image
				$("#payment_loading").show();
				
				//send request to the purchase service
				$.ajax({
					url:"ws/purchaseCredit.py",
					data:{
						email:app.userInfo.email,
						oauth:app.userInfo.oauth,
						plan:plan,
						card_name:card_name,
						card_number:card_number,
						card_expiryDate:expiryDate,
						card_authNumber:card_authNumber
					},
					method:"post",
					dataType:"json",
					success:function(result){
						//hide loading image
						$("#payment_loading").hide();
						
						console.log(result);
						//if error
						if(result.status && result.status=='error'){
							showPaymentMsg(result.msg);
							return; 
						}

					},
					error:function(error){
						console.log(error);
						showPaymentMsg(error.responseText)
						//hide loading image
						$("#payment_loading").hide();
					}
				})
				
			}else{
				showPaymentMsg('Please input the correct credit card number.');
				$('#payment_cardNumber').focus();
				return;
			}
		}
	}else{
		showPaymentMsg('Cardholder name, number, expiryMonth, or security code is blank. Please check it again.');
	}
}



//show payment msg
function showPaymentMsg(msg){
	$("#payment_msg").html(msg);
	//hide loading image
	$("#payment_loading").hide();
}



//change other plan
function changePlan(){
	//redirect to accountManagement.html
	window.location.href='accountManagement.html?email='+app.userInfo.email+'&tab=upgrade';
}


//get url parameter
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}
