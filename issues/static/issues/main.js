// Simple polling for unread count
function updateUnread(){
fetch('/issues/api/unread-count/')
.then(r => r.json())
.then(data => {
const el = document.getElementById('unread-count');
if(el) el.innerText = data.unread;
}).catch(e=>{});
}
setInterval(updateUnread, 30000);
updateUnread();