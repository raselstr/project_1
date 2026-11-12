/**
 * Custom JavaScript for Tech Modern Theme & Mobile Responsive
 * v5.6 — Sidebar accordion fix + active state URL matching
 */

"use strict";

$(document).ready(function() {

  // =========================================================================
  // 1. SIDEBAR ACCORDION & ACTIVE STATE
  // =========================================================================
  function initSidebarActiveState() {
    var currentUrl = window.location.href;
    var currentPath = window.location.pathname.replace(/\/+$/, "");
    var currentSearch = window.location.search;
    var currentParams = new URLSearchParams(currentSearch);
    var currentSubmenuId = currentParams.get('submenu_id');

    var $bestMatch = null;
    var bestScore = -1;

    // Cari submenu yang paling cocok dengan URL saat ini
    $('.sidebar-menu li.dropdown ul.dropdown-menu li a.nav-link').each(function() {
      var $link = $(this);
      var href = $link.attr('href') || '';
      if (!href || href === '#' || href.indexOf('javascript:') === 0) return;

      var linkUrl;
      try {
        linkUrl = new URL(href, window.location.origin);
      } catch(e) {
        return;
      }

      var linkPath = linkUrl.pathname.replace(/\/+$/, "");
      var linkSubmenuId = linkUrl.searchParams.get('submenu_id');
      var score = 0;

      // 1. Jika submenu_id sama persis: skor tertinggi (100)
      if (currentSubmenuId && linkSubmenuId && currentSubmenuId === linkSubmenuId) {
        score += 100;
      }

      // 2. Jika pathname sama persis (skor 50)
      if (currentPath && linkPath && currentPath === linkPath) {
        score += 50;
      }
      // 3. Jika pathname merupakan awalan (misal currentPath = /pendidikan/rencana/list, linkPath = /pendidikan/rencana) (skor 30)
      else if (linkPath && linkPath !== '' && linkPath !== '/' && currentPath.indexOf(linkPath) === 0) {
        score += 30;
      }

      if (score > bestScore && score > 0) {
        bestScore = score;
        $bestMatch = $link;
      }
    });

    // Fallback: Dashboard utama jika di root path
    if (!bestScore || bestScore <= 0) {
      if (currentPath === '' || currentPath === '/' || currentPath === '/dashboard') {
        var $dashLink = $('.sidebar-menu a[href*="dashboard"]').first();
        if ($dashLink.length) {
          $bestMatch = $dashLink;
          bestScore = 10;
        }
      }
    }

    // Terapkan active state
    if ($bestMatch && bestScore > 0) {
      // Bersihkan semua active dan tutup dropdown lain
      $('.sidebar-menu li.dropdown').removeClass('active open-temp');
      $('.sidebar-menu li.dropdown ul.dropdown-menu li').removeClass('active');
      $('.sidebar-menu li.dropdown ul.dropdown-menu').hide();

      // Tandai submenu item sebagai active
      var $subLi = $bestMatch.closest('li');
      $subLi.addClass('active');

      // Tandai parent menu dropdown sebagai active dan buka menunya
      var $parentDropdown = $bestMatch.closest('li.dropdown');
      $parentDropdown.addClass('active');
      $parentDropdown.find('> ul.dropdown-menu').show();
    }
  }

  initSidebarActiveState();

  // Handler saat user mengklik submenu item
  $(document).on('click', '.sidebar-menu ul.dropdown-menu li a.nav-link', function() {
    var $link = $(this);
    $('.sidebar-menu ul.dropdown-menu li').removeClass('active');
    $link.closest('li').addClass('active');

    var $parentDropdown = $link.closest('li.dropdown');
    $('.sidebar-menu li.dropdown').not($parentDropdown).removeClass('active open-temp');
    $parentDropdown.addClass('active');
  });

  // =========================================================================
  // 2. Mobile Sidebar State Management
  // =========================================================================
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
  // Memastikan semua tabel data memiliki scrollbar horizontal, KECUALI tabel di dalam card summary (.card-large-icons)
  function applyTableResponsive(context) {
    var $root = context ? $(context) : $(document);

    // Lepas pembungkus table-responsive jika membungkus tabel di dalam card-large-icons
    $root.find('.card-large-icons .table-responsive > table').unwrap();

    $root.find('table').each(function() {
      var $t = $(this);
      // Lewati tabel di dalam card-large-icons atau yang sudah berada dalam container scrollable
      if ($t.closest('.card-large-icons, .card-icon, .table-responsive, .dataTables_wrapper, .dataTables_scrollBody, .sp2d-table-wrapper, .table-container').length) {
        return;
      }
      $t.wrap('<div class="table-responsive"></div>');
    });

    // Inisialisasi indikator scroll jika tabel data meluap
    $('.table-responsive, .dataTables_scrollBody, .sp2d-table-wrapper, .table-container').not('.card-large-icons *').each(function() {
      var el = this;
      if (el.scrollWidth > el.clientWidth) {
        $(el).addClass('has-horizontal-scroll');
      } else {
        $(el).removeClass('has-horizontal-scroll');
      }
    });
  }

  // 3. Mobile Button Text & Icon Adapter
  // Memperbaiki tombol di layar HP/Android agar teks ringkas, tidak meluap, dan icon selalu ada
  function adaptMobileButtons(context) {
    var $root = context ? $(context) : $(document);

    // Cari tombol di card-header, card-header-action, btn-group
    $root.find('.card-header-action .btn, .card-header .btn, .btn-group .btn').each(function() {
      var $btn = $(this);
      if ($btn.data('mobile-icon-adapted')) return;

      var fullText = $.trim($btn.text());
      if (!fullText) return;

      // Simpan teks asli sebagai title atribut untuk tooltip di HP (tap & hold)
      if (!$btn.attr('title')) {
        $btn.attr('title', fullText);
      }

      var hasIcon = $btn.find('i, svg').length > 0;
      var lower = fullText.toLowerCase();

      // Tambahkan ikon jika belum ada
      if (!hasIcon) {
        var iconClass = '';
        if (lower.indexOf('kembali') !== -1) {
          iconClass = 'fas fa-arrow-left';
        } else if (lower.indexOf('excel') !== -1) {
          iconClass = 'fas fa-file-excel';
        } else if (lower.indexOf('sp2d') !== -1) {
          iconClass = 'fas fa-file-invoice';
        } else if (lower.indexOf('reviu') !== -1) {
          iconClass = 'fas fa-clipboard-check';
        } else if (lower.indexOf('cetak') !== -1) {
          iconClass = 'fas fa-print';
        } else if (lower.indexOf('tambah') !== -1 || lower.indexOf('simpan') !== -1 || lower.indexOf('input') !== -1) {
          iconClass = 'fas fa-plus';
        } else if (lower.indexOf('posting') !== -1) {
          iconClass = 'fas fa-paper-plane';
        } else if (lower.indexOf('batal') !== -1) {
          iconClass = 'fas fa-times';
        } else if (lower.indexOf('filter') !== -1) {
          iconClass = 'fas fa-filter';
        }

        if (iconClass) {
          $btn.prepend('<i class="' + iconClass + '"></i> ');
        }
      }

      // Bungkus text node ke dalam span.btn-text agar bisa diatur CSS ellipsis di HP
      $btn.contents().filter(function() {
        return this.nodeType === 3 && $.trim(this.nodeValue).length > 0;
      }).each(function() {
        var txt = $.trim(this.nodeValue);
        // Persingkat teks umum yang terlalu panjang di tombol mobile
        if (txt.toLowerCase().indexOf('tambah perencanaan sisa') !== -1) {
          txt = 'Tambah Sisa';
        } else if (txt.toLowerCase().indexOf('tambah perencanaan') !== -1) {
          txt = 'Tambah';
        } else if (txt.toLowerCase().indexOf('tambah realisasi sisa') !== -1) {
          txt = 'Tambah Sisa';
        } else if (txt.toLowerCase().indexOf('tambah realisasi') !== -1) {
          txt = 'Tambah';
        } else if (txt.toLowerCase().indexOf('cetak daftar sp2d') !== -1) {
          txt = 'SP2D';
        } else if (txt.toLowerCase().indexOf('cetak hasil reviu') !== -1) {
          txt = 'Reviu';
        }
        $(this).replaceWith('<span class="btn-text">' + txt + '</span>');
      });

      $btn.data('mobile-icon-adapted', true);
    });

    // Berikan class penanda pada baris persentase di card summary
    $root.find('.card.card-large-icons .table tr').each(function() {
      var rowText = $(this).text();
      if (rowText.indexOf('%') !== -1 || rowText.toLowerCase().indexOf('persentase') !== -1) {
        $(this).addClass('stat-percentage-row');
      }
    });
  }

  // 4. Executive Home Cards Enhancement (Desktop & Mobile)
  function enhanceHomeCards(context) {
    var $root = context ? $(context) : $(document);

    $root.find('.card.card-large-icons').each(function() {
      var $card = $(this);
      if ($card.data('desktop-enhanced')) return;

      var $body = $card.find('.card-body');
      var $h4 = $body.find('h4').first();
      var h4Text = $.trim($h4.text());

      // Tambahkan badge status pada judul h4 jika belum ada
      if ($h4.length && !$h4.find('.card-type-badge').length) {
        var badgeText = 'DAU SG';
        var badgeClass = 'badge-primary';
        var lower = h4Text.toLowerCase();
        if (lower.indexOf('sisa') !== -1) {
          badgeText = 'Sisa Tahun Lalu';
          badgeClass = 'badge-info';
        } else if (lower.indexOf('induk') !== -1 || lower.indexOf('berjalan') !== -1 || lower.indexOf('rencana') !== -1) {
          badgeText = 'Tahun Berjalan';
          badgeClass = 'badge-primary';
        }
        $h4.html(h4Text + ' <span class="card-type-badge badge ' + badgeClass + ' ml-2"><i class="fas fa-check-circle mr-1"></i>' + badgeText + '</span>');
      }

      // Header strip decorative tech pill
      var $icon = $card.find('.card-icon');
      if ($icon.length && !$icon.find('.card-header-badge').length) {
        $icon.append('<div class="card-header-badge"><span class="tech-dot mr-1"></span>TKDD ASAHAN</div>');
      }

      // Tambahkan visual progress bar pada baris persentase
      $card.find('.table tr').each(function() {
        var $row = $(this);
        var text = $row.text();
        var match = text.match(/(\d+[\.,]?\d*)\s*%/);
        if (match && !$row.find('.progress-bar-wrap').length) {
          var pct = parseFloat(match[1].replace(',', '.'));
          if (!isNaN(pct)) {
            var displayPct = pct > 100 ? 100 : (pct < 0 ? 0 : pct);
            var barColor = pct >= 80 ? 'linear-gradient(90deg, #059669, #10b981)' : (pct >= 50 ? 'linear-gradient(90deg, #0052cc, #38bdf8)' : 'linear-gradient(90deg, #d97706, #fbbf24)');
            var $lastTd = $row.find('td:last-child');
            $lastTd.append(
              '<div class="progress-bar-wrap mt-1" style="height: 5px; width: 100%; max-width: 140px; min-width: 60px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-left: auto;">' +
                '<div style="height: 100%; width: ' + displayPct + '%; background: ' + barColor + '; border-radius: 4px; transition: width 0.8s ease;"></div>' +
              '</div>'
            );
          }
        }
      });

      $card.data('desktop-enhanced', true);
    });
  }

  applyTableResponsive();
  adaptMobileButtons();
  enhanceHomeCards();

  // Re-run adapter saat terjadi event htmx swap atau window resize
  if (document.body) {
    document.body.addEventListener('htmx:afterSwap', function(evt) {
      applyTableResponsive(evt.detail.target);
      adaptMobileButtons(evt.detail.target);
      enhanceHomeCards(evt.detail.target);
    });
  }

  $(window).on('resize', function() {
    $('.table-responsive, .dataTables_scrollBody, .sp2d-table-wrapper, .table-container').each(function() {
      var el = this;
      if (el.scrollWidth > el.clientWidth) {
        $(el).addClass('has-horizontal-scroll');
      } else {
        $(el).removeClass('has-horizontal-scroll');
      }
    });
    adaptMobileButtons();
    enhanceHomeCards();
  });

});
