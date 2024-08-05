function camel2title(str){
    let result = str                                    
    .replace(/(_)+/g, ' ')                              
    .replace(/([a-z])([A-Z][a-z])/g, "$1 $2")
    .replace(/([A-Z][a-z])([A-Z])/g, "$1 $2")
    .replace(/([a-z])([A-Z]+[a-z])/g, "$1 $2")
    .replace(/([A-Z]+)([A-Z][a-z][a-z])/g, "$1 $2")
    .replace(/([a-z]+)([A-Z0-9]+)/g, "$1 $2")
    // Note: the next regex includes a special case to exclude plurals of acronyms, e.g. "ABCs"
    .replace(/([A-Z]+)([A-Z][a-rt-z][a-z]*)/g, "$1 $2") 
    .replace(/([0-9])([A-Z][a-z]+)/g, "$1 $2")          
    // Note: the next two regexes use {2,} instead of + to add space on phrases like Room26A and 26ABCs but not on phrases like R2D2 and C3PO"
    .replace(/([A-Z]{2,})([0-9]{2,})/g, "$1 $2")
    .replace(/([0-9]{2,})([A-Z]{2,})/g, "$1 $2")
    .trim();
    // capitalize the first letter
    return result.charAt(0).toUpperCase() + result.slice(1);
}

function notify(status, title, text, settings={}){
    let defaults = {
        status: status,
        title: title,
        text: text,
        effect: 'slide',
        autoclose: true,
        autotimeout: 3000,
        type: 2,
        position: 'bottom x-center'
    }
    settings = {...defaults, ...settings};
    let not = new Notify(settings);
    return not
}