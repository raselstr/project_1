/**
 * Custom JavaScript for Tech Modern Theme & Mobile Responsive
 * v5.4 — Sidebar dipindah ke luar #app, backdrop di root stacking context
 */

"use strict";

$(document).ready(function() {

  // 1. Mobile Sidebar State Management
  function handleMobileSidebar() {
    if ($(window).outerWidth() <= 1024) {
      if (!$('body').hasClass('sidebar-show')) {
        $('body').addClass('sidebar-gone');
      }
    } else {
      $('body').removeClass('sidebar-gone sidebar-show');
    }
  }

  handleMobileSidebar();
  $(window).on('resize', handleMobileSidebar);

  // Klik atau tap pada backdrop menutup sidebar
  $(document).on('click touchstart', '.sidebar-backdrop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    $('body').removeClass('sidebar-show').addClass('sidebar-gone');
  });

  // Pastikan klik di luar sidebar menutup sidebar (fallback)
  $(document).on('click', function(e) {
    if ($('body').hasClass('sidebar-show') && $(window).outerWidth() <= 1024) {
      if (!$(e.target).closest('.main-sidebar, [data-toggle="sidebar"]').length) {
        $('body').removeClass('sidebar-show').addClass('sidebar-gone');
      }
    }
  });

  // 2. Universal Table Responsive Wrapper
  // Memastikan semua tabel (termasuk yang digenerate dinamik) memiliki scrollbar horizontal
  function applyTableResponsive(context) {
    var $root = context ? $(context) : $(document);
    $root.find('table').each(function() {
      var $t = $(this);
      // Lewati tabel yang sudah berada dalam container scrollable
      if ($t.closest('.table-responsive, .dataTables_wrapper, .dataTables_scrollBody, .sp2d-table-wrapper').length) {
        return;
      }
      $t.wrap('<div class="table-responsive"></div>');
    });

    // Inisialisasi indikator scroll jika tabel meluap
    $('.table-responsive, .dataTables_scrollBody, .sp2d-table-wrapper').each(function() {
      var el = this;
      if (el.scrollWidth > el.clientWidth) {
        $(el).addClass('has-horizontal-scroll');
      }
    });
  }

  applyTableResponsive();

  // Re-run wrapper saat terjadi event htmx swap atau window resize
  if (document.body) {
    document.body.addEventListener('htmx:afterSwap', function(evt) {
      applyTableResponsive(evt.detail.target);
    });
  }

  $(window).on('resize', function() {
    $('.table-responsive, .dataTables_scrollBody, .sp2d-table-wrapper').each(function() {
      var el = this;
      if (el.scrollWidth > el.clientWidth) {
        $(el).addClass('has-horizontal-scroll');
      } else {
        $(el).removeClass('has-horizontal-scroll');
      }
    });
  });

});
