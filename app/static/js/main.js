'use strict';
// Melhorias de usabilidade sem dependências externas.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-auto-submit]').forEach(control => {
    control.addEventListener('change', () => control.form?.requestSubmit());
  });
  document.querySelectorAll('.flash-close').forEach(button => {
    button.addEventListener('click', () => button.closest('.flash')?.remove());
  });
  document.querySelectorAll('[data-confirm-return]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm(form.getAttribute('data-confirm-return'))) event.preventDefault();
    });
  });
});
