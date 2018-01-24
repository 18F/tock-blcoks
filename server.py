import argparse
import tock_blocks
import utilization_summary

def main():
    parser = argparse.ArgumentParser(description='Calculate a users major time blocks')
    parser.add_argument('-p','--program',
                        help='choose between tock blocks and the full user program.',
                        default='util-csv',
                        dest='program')
    parser.add_argument('-u','--users', nargs='+',
                        help='user or users list',
                        default='darren.divens',
                        dest='users')
    parser.add_argument('-f', action='store',
                        dest='file',
                        help='The csv file for the tock entries')
    parser.add_argument('-s', action='store', default='2016-01-01',
                        dest='start_date',
                        help='YYYY-MM-DD The start date of the tock entries you would like to search through.')
    parser.add_argument('-e', action='store', default='2016-06-01',
                        dest='end_date',
                        help='YYYY-MM-DD The end date of the tock entries you would like to search through.')
    parser.add_argument('-d', '--display_format',
                        dest='display_format',
                        help='print display in pretty colors on standard out, or in markdown')
    parser.add_argument('-n','--no-leave', action='store_true',
                        default=False,
                        dest='exclude_leave',
                        help='exclude annual leave and holidays from the report')
    parser.add_argument('-o','--outfile',
                        dest='outfile',
                        help='outfile for util summary')
    parser.add_argument('-b','--beginmonth',
                        dest='beginmonth',
                        help='starting month for the utilization summary')
    parser.add_argument('-l','--lastmonth',
                        dest='lastmonth',
                        help='last or ending month for the utilization summary')


    args = parser.parse_args()
    if (args.program == 'tock-blocks'):
        if(args.display_format == 'pretty'):
            print("Tock data from "+args.start_date + " to "+args.end_date)
        if(args.display_format == 'markdown'):
            print("# Tock data from "+args.start_date + " to "+args.end_date)
        tock_blocks.block_by_array(args.users, args.start_date, args.end_date, args.display_format, args.exclude_leave)
    elif (args.program == 'util-csv'):
        utilization_summary.all_users_from_file("users.csv", args)

if __name__ == "__main__":
    main()
