window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};
window.onload = _ => document.querySelectorAll('.delete').forEach(el => {
  el.onclick = function(e) {
    if (confirm("Do you really want to delete?")) {
      fetch(window.location, { method: 'DELETE' })
      .then(i => i.json())
      .then(r => {
      console.log(r)
        if (r.success)
          window.location = '/'
        else
          alert("An error occurred!")
      }
    }
  };
});
