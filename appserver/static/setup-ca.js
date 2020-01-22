require(["splunkjs/mvc/searchmanager", 
             "jquery","splunkjs/mvc",
       "splunkjs/mvc/tokenutils", "splunkjs/mvc/simplexml/ready!"],
  function(SearchManager, $, mvc){
   let d = new Date();
   console.log("debuuger says: v2", d);

   let defaultTokMod = mvc.Components.get("default")

   $('#my-btn').click(()=>{
    let caname = $('#caname').val();
    let pw = $('#pw').val()
    console.log(caname, pw);
    defaultTokMod.set({'canametok':caname});
    defaultTokMod.set({'pwtok':pw});
   });

  

   $('#submit-btn').click(()=>{
    alert("submit cliked");
   });
});
