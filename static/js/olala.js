// Confirmaciones de eliminación
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.btn-eliminar').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm('¿Está seguro que desea eliminar este elemento?')) {
        e.preventDefault();
      }
    });
  });

  // Auto-dismiss alerts
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (a) {
      var bsAlert = new bootstrap.Alert(a);
      bsAlert.close();
    });
  }, 5000);
});
