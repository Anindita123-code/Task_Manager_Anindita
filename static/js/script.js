 $(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"})
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('.datepicker').datepicker({
        format: "dd mmmm, yyyy",
        showClearBtn: true,
        yearRange: 3,
        i18n:{
            done: "Select"
        }
    });
});