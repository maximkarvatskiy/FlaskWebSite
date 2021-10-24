function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function updateNote(noteId) {
  fetch("/update-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  })
}

function likeNote(noteId) {
  fetch("/like-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/news";
  });
}