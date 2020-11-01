import sys

import click

from . import data, get_data_dir
from .manual import edit_manual_balances


@click.group()
def main() -> None:
    """
    Interact with my budget!
    """
    pass


@main.command()
def edit_manual() -> None:
    """
    Edit the manual balances file
    """
    ddir = get_data_dir()
    assert ddir.is_dir() and ddir.exists()

    edit_manual_balances(ddir / "manual_balances.csv")
    sys.exit(0)


# TODO: split this into further commands?
@main.command()
@click.option(
    "--graph", default=False, is_flag=True, help="Show the graph of balance history"
)
@click.option("--repl", default=False, is_flag=True, help="Drop into repl")
@click.option("--df", default=False, is_flag=True, help="Use dataframe in REPL")
def accounts(graph: bool, repl: bool, df: bool) -> None:
    """
    Show a summary/graph of the current/past accounts balances
    """

    from .analyze.balance_history import graph_account_balances

    if graph:
        account_snapshots, _ = data()
        account_snapshots.sort(key=lambda s: s.at)
        graph_account_balances(account_snapshots, graph)
        sys.exit(0)
    if repl or df:
        import IPython  # type: ignore[import]
        from .analyze import cleaned_snapshots, cleaned_snapshots_df

        click.secho("Use 'snapshots' to interact with data", fg="green")
        if df:
            snapshots = cleaned_snapshots_df()
        else:
            # TODO(sean): fix timestamp
            snapshots = list(cleaned_snapshots())  # type: ignore[assignment,arg-type]
        IPython.embed()
        sys.exit(0)
    click.echo("(No Flag Provided)")


@main.command()
@click.option(
    "--repl",
    is_flag=True,
    default=False,
    help="Drop into a repl with access to the accounts/spending",
)
def summary(repl: bool) -> None:
    """
    Prints a summary of current accounts/recent transactions
    """

    from .analyze.summary import recent_spending, account_summary

    account_snapshots, transactions = data()

    spend = recent_spending(transactions)
    acc = account_summary(account_snapshots)

    # sort by date
    spend.sort_values(["on"], inplace=True)

    if repl:
        click.secho("Use 'acc' and 'spend' to interact", fg="green")
        import IPython  # type: ignore

        IPython.embed()


if __name__ == "__main__":
    main()
