require(["splunkjs/mvc/searchmanager", 
       "jquery","splunkjs/mvc",
       "splunkjs/mvc/tokenutils", 
       "splunkjs/mvc/simplexml/ready!"],
  function(SearchManager, $, mvc){
   var submited = 0;
   let d = new Date();
   console.log("debuuger says: v4", d);
   if($('#cbconf').prop('checked') == true){
      $('#useconf').show();
      $('#usefields').hide();
   } 

   $('#cbconf').change(function(){
      $('#useconf').toggle();
      $('#usefields').toggle();
   });
   let defaultTokMod = mvc.Components.get("default")

   $('#submit-btn').click(()=>{
    let caname = $('#caname').val();
    let pw = $('#pw').val()
    let C =  $('#C').val();
    let ST =  $('#ST').val();
    let L =  $('#L').val();
    let O =  $('#O').val();
    let OU =  $('#OU').val();
    let CN =  $('#CN').val();
    let email =  $('#email').val();
    let confpath = $('#confpath').val();
    
   
    let search = $('#cbconf').prop('checked') == true ? `|script generate-ca-certs cbconf=1 confpath=${confpath}`:
      `|script generate-ca-certs cbconf=0 caname=${caname} capw=${pw} subjstr=/C=${C}/ST=${ST}/L=${L}/O=${O}/OU=${OU}/CN=${CN} email=${email}`
    console.log(search);

    let sm = new SearchManager({
            id: `submit-ca${submited}`,
            earliest: "-1s",
            latest: "now",
            preview: "false",
            cache: "false",
            search: search
      });
      
      let smres = mvc.Components.get(`submit-ca${submited}`);
      console.log(smres);
      submited++;
      
      
      
   });

});


