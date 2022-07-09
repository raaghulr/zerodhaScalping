import GUI_kite as gk
import sys

def main() -> int:
    """
    `cli_args` makes it possible to call this function command-line-style
    from other Python code without touching sys.argv.
    """
    try:
        print("Success")

    except KeyboardInterrupt:
        print('Aborted manually.', file=sys.stderr)
        return 1

    except Exception as err:
        # (in real code the `except` would probably be less broad)
        # Turn exceptions into appropriate logs and/or console output.

        # non-zero return code to signal error
        # Can of course be more fine grained than this general
        # "something went wrong" code.
        print("Exception %s " % str(err))
        return 1

    return 0  # success

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gk.startUI()
    print('End of GUI')
    sys.exit(0)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
