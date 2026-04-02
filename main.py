from dotenv import load_dotenv
load_dotenv()

import subprocess
import sys
import os

from app2.config.imports import (
    get_theme,
    get_theme_style,
    console,
    Text,
    Panel,
    live_loading,
    pause,
    print_error,
    print_panel,
    print_warning,
    check_for_updates,
    ensure_git
)

def is_rebase_in_progress() -> bool:
    """Memeriksa apakah proses rebase sedang berjalan."""
    return os.path.exists(".git/rebase-apply") or os.path.exists(".git/rebase-merge")

def git_pull_rebase() -> None:
    """Menjalankan git pull --rebase, fallback ke reset jika gagal."""
    theme = get_theme()
    result = {"status": None, "error": None, "output": ""}

    if is_rebase_in_progress():
        text = Text.from_markup(
            "[bold yellow]Rebase masih berlangsung[/]\n\n"
            f"[{get_theme_style('text_warning')}]Selesaikan dengan `git rebase --continue` atau batalkan dengan `git rebase --abort`[/]"
        )
        console.print(Panel(
            text,
            title=f"[{get_theme_style('text_title')}]Update CLI[/]",
            border_style=get_theme_style("border_warning"),
            padding=(1, 2),
            expand=True
        ))
        pause()
        sys.exit(1)

    def run_git_pull():
        try:
            subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True, stdout=subprocess.DEVNULL)
            output = subprocess.run(
                ['git', 'pull', '--rebase'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            result["status"] = "success"
            result["output"] = output.stdout.strip()
        except subprocess.CalledProcessError as e:
            result["status"] = "fail"
            result["error"] = f"Git pull gagal: {e.stderr.strip()}"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

    def run_git_reset():
        try:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
            subprocess.run(['git', 'fetch'], check=True, stdout=subprocess.DEVNULL)
            reset_output = subprocess.run(
                ['git', 'reset', '--hard', f'origin/{branch}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            result["status"] = "reset"
            result["output"] = reset_output.stdout.strip()
        except Exception as e:
            result["status"] = "reset_fail"
            result["error"] = str(e)

    with live_loading("Menarik pembaruan dari repository...", theme):
        run_git_pull()

    if result["status"] == "success":
        text = Text.from_markup(
            f"[bold {get_theme_style('text_date')}]Git pull berhasil[/]\n\n[{get_theme_style('text_body')}]{result['output']}[/]"
        )
        console.print(Panel(
            text,
            title=f"[{get_theme_style('text_title')}]Update CLI[/]",
            border_style=get_theme_style("border_info"),
            padding=(1, 2),
            expand=True
        ))

    elif result["status"] == "fail":
        text = Text.from_markup(
            f"[bold {get_theme_style('text_error')}]Git pull gagal[/]\n\n[{get_theme_style('text_error')}]{result['error']}[/]\n\n[{get_theme_style('text_warning')}]Silakan coba reset paksa terlebih dahulu[/]"
        )
        console.print(Panel(
            text,
            title=f"[{get_theme_style('text_title')}]Update CLI[/]",
            border_style=get_theme_style("border_error"),
            padding=(1, 2),
            expand=True
        ))

        with live_loading("Melakukan reset ke origin...", theme):
            run_git_reset()

        if result["status"] == "reset":
            text = Text.from_markup(
                f"[bold {get_theme_style('text_success')}]Reset berhasil, repository telah sinkron dengan origin[/]\n\n[{get_theme_style('text_body')}]{result['output']}[/]"
            )
            console.print(Panel(
                text,
                title=f"[{get_theme_style('text_title')}]Update CLI[/]",
                border_style=get_theme_style("border_success"),
                padding=(1, 2),
                expand=True
            ))
        else:
            text = Text.from_markup(
                f"[bold {get_theme_style('text_error')}]Reset gagal[/]\n\n[{get_theme_style('text_error')}]{result['error']}[/]"
            )
            console.print(Panel(
                text,
                title=f"[{get_theme_style('text_title')}]Update CLI[/]",
                border_style=get_theme_style("border_error"),
                padding=(1, 2),
                expand=True
            ))
            pause()
            sys.exit(1)

    else:
        text = Text.from_markup(
            f"[bold {get_theme_style('text_warning')}]Terjadi kesalahan saat git pull[/]\n\n[{get_theme_style('text_warning')}]{result['error']}[/]"
        )
        console.print(Panel(
            text,
            title=f"[{get_theme_style('text_title')}]Update CLI[/]",
            border_style=get_theme_style("border_warning"),
            padding=(1, 2),
            expand=True
        ))
        pause()
        sys.exit(1)

def run_menu() -> None:
    """Menampilkan menu pilihan mode CLI dan menjalankan modul yang dipilih."""
    text = Text.from_markup(
        f"[bold {get_theme_style('text_title')}]Pilih Mode CLI[/]\n\n"
        f"[{get_theme_style('text_body')}] [1.] Default (Tanpa Tema)[/]\n"
        f"[{get_theme_style('text_body')}] [2.] Formal (Mode Minimalis)[/]\n"
        f"[{get_theme_style('text_body')}] [3.] Tongkrongan (Full emoji)[/]\n"
    )
    console.print(Panel(
        text,
        border_style=get_theme_style("border_info"),
        padding=(0, 2),
        expand=True
    ))

    choice = input("Masukkan pilihan [1/2/3]: ").strip()

    mode_modules = {
        "1": "master1",
        "2": "master2",
        "3": "master3"
    }

    selected_module = mode_modules.get(choice, "master2")

    try:
        master = __import__(selected_module)
        master.main()
    except ImportError as e:
        print_error("Kesalahan", f"Mode {selected_module} tidak tersedia: {e}")
        pause()
        sys.exit(1)
    except KeyboardInterrupt:
        print_panel("Keluar", "Aplikasi dihentikan oleh pengguna", border_style=get_theme_style("border_info"))
        sys.exit(0)
    except Exception as e:
        print_error("Kesalahan", f"Gagal menjalankan aplikasi | {type(e).__name__} - {e}")
        pause()
        sys.exit(1)

if __name__ == "__main__":
    """Entry point aplikasi: cek update → pull → jalankan menu."""
    try:
        with live_loading("Memeriksa pembaruan...", get_theme()):
            need_update = check_for_updates()
    except Exception as e:
        print_warning("Kesalahan", f"Gagal memeriksa pembaruan: {e}")
        need_update = False

    ensure_git()
    if need_update:
        git_pull_rebase()

    run_menu()