"""
This script implements the main command-line interface to the CEA. It allows running the various scripts through a
standard interface.
"""
import os
import sys


def demand(args):
    """Run the demand script with the arguments provided."""
    import cea.demand.demand_main
    cea.demand.demand_main.run_as_script(scenario_path=args.scenario, weather_path=args.weather)


def demand_helper(args):
    """Run the demand helper script with the arguments provided."""
    import cea.demand.preprocessing.properties
    cea.demand.preprocessing.properties.run_as_script(scenario_path=args.scenario,
                                                      prop_thermal_flag='thermal' in args.archetypes,
                                                      prop_architecture_flag='architecture' in args.archetypes,
                                                      prop_hvac_flag='HVAC' in args.archetypes,
                                                      prop_comfort_flag='comfort' in args.archetypes,
                                                      prop_internal_loads_flag='internal-loads' in args.archetypes)


def benchmark_graphs(args):
    """Run the benchmark graphs script with the arguments provided."""
    import cea.analysis.benchmark
    import cea.inputlocator
    locator_list = [cea.inputlocator.InputLocator(scenario) for scenario in args.scenarios]
    cea.analysis.benchmark.benchmark(locator_list=locator_list, output_file=args.output_file)


def weather_files(_):
    """List the available weather files to STDOUT."""
    import cea.inputlocator
    weather_names = cea.inputlocator.InputLocator(None).get_weather_names()
    for weather_name in weather_names:
        print(weather_name)


def weather_path(args):
    """Find the path to the weather file by name"""
    import cea.inputlocator
    weather_path = cea.inputlocator.InputLocator(None).get_weather(args.weather)
    print(weather_path)


def file_location(args):
    """Locate a file using the InputLocator. The file to find is named the same as the InputLocator
    attribute."""
    import cea.inputlocator
    locator = cea.inputlocator.InputLocator(args.scenario)
    print(getattr(locator, args.attribute)())


def main():
    """Parse the arguments and run the program."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scenario', help='Path to the scenario folder', default=os.curdir)
    subparsers = parser.add_subparsers()

    demand_parser = subparsers.add_parser('demand')
    demand_parser.add_argument('-w', '--weather', help='Path to the weather file')
    demand_parser.set_defaults(func=demand)

    demand_helper_parser = subparsers.add_parser('demand-helper')
    demand_helper_parser.add_argument('--archetypes', help='List of archetypes process', nargs="*",
                                      default=['thermal', 'comfort', 'architecture', 'HVAC', 'internal-loads'],
                                      choices=['thermal', 'comfort', 'architecture', 'HVAC', 'internal-loads'])
    demand_helper_parser.set_defaults(func=demand_helper)

    benchmark_graphs_parser = subparsers.add_parser('benchmark-graphs')
    benchmark_graphs_parser.add_argument('--output-file', help='File (*.pdf) to store the output in')
    benchmark_graphs_parser.add_argument('--scenarios', help='List of scenarios to benchmark',
                                         nargs='+', default=['.'])
    benchmark_graphs_parser.set_defaults(func=benchmark_graphs)

    weather_files_parser = subparsers.add_parser('weather-files')
    weather_files_parser.set_defaults(func=weather_files)

    weather_path_parser = subparsers.add_parser('weather-path')
    weather_path_parser.add_argument('weather', metavar='ATTR',
                                     help='The name of the weather file (from the weather-files list)')
    weather_path_parser.set_defaults(func=weather_path)

    file_location_parser = subparsers.add_parser('locate')
    file_location_parser.add_argument('attribute', metavar='ATTR',
                                      help='The name of the file to find, denoted by InputLocator.ATTR()')
    file_location_parser.set_defaults(func=file_location)

    parsed_args = parser.parse_args()
    parsed_args.func(parsed_args)


if __name__ == '__main__':
    main()
