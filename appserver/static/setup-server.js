require(["splunkjs/mvc/searchmanager", 
       "jquery","splunkjs/mvc",
       "splunkjs/mvc/tokenutils", 
       "splunkjs/mvc/simplexml/ready!"],
  function(SearchManager, $, mvc){
      var submited = 0;
      let d = new Date();
      console.log("debuuger says: v1", d);

      function caCertExists(){
         console.log("checking if ca already generated");
         let jobid = "ca-exists-check";
         let caSM = new SearchManager({
            id: jobid,
            earliest: "-10s",
            latest: "now",
            preview: "false",
            cache: "false",
            search: "|script ca-exists-check"
         });
         console.log(caSM);
         let mainsearch = mvc.Components.get(jobid);
         let myResult = mainsearch.data("results");
         var  printed_data = false;
         myResult.on("data", function(){
            console.log("data",myResult.data());
            console.log("has data",myResult.hasData());
            
            console.log("printed data first time", printed_data);
            if(printed_data === false){
               let rows = myResult.data().rows;
               if(rows[0][0] === "none"){
                  $('#CAexists').addClass('label-warning');
                  $('#CAexists').html('<p>Create CA certificate first!</p>');
               }else{
                  $('#CAexists').addClass('label-success').html('<form><fieldset><ul id="ca-list">');
                  for(let i=0;i < rows.length; i++){
                     $('#ca-list').append(`<li><label><input type="radio" class="ca-radio" name="ca-radios" value="${rows[i][0]}"> ${rows[i][0]} </label></li>`);
                  }
                  $('#CAexists').append('</ul></fieldset></form>');
                  $('#submit-btn').show();
                  printed_Data = true;   
               }
            }            
         });
      }

      caCertExists();
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

         if($('.ca-radio:checked').length === 0){
            alert("select a CA first!");
            return;
         }
         $('.ca-radio:checked').each(function (){
            console.log($(this).val());
         });
         
         let search = $('#cbconf').prop('checked') == true ? `|script generate-server-certs cbconf=1 confpath=${confpath}`:
            `|script generate-server-certs cbconf=0 caname=${caname} capw=${pw} subjstr=/C=${C}/ST=${ST}/L=${L}/O=${O}/OU=${OU}/CN=${CN} email=${email}`
         console.log(search);
   /*
       let sm = new SearchManager({
               id: `submit-server${submited}`,
               earliest: "-1s",
               latest: "now",
               preview: "false",
               cache: "false",
               search: search
         });
         
         let smres = mvc.Components.get(`submit-cservera${submited}`);
         console.log(smres);
         submited++;
       */  
         
         
      });
   

});



