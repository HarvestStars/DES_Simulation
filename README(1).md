# DES_Simulation

A Discrete Event Simulation (DES) framework built in Python. This project is designed to simulate dynamic systems where state changes occur at discrete points in time. The simulation uses a flexible and extensible design, allowing users to model and analyze various processes.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **Event-Driven Architecture:** Supports dynamic systems with discrete state transitions.
- **Customizable Events:** Users can define custom events and processes for their simulation scenarios.
- **Efficient Execution:** Uses Python's generator functions to pause and resume processes dynamically.
- **Extensibility:** Easily extend or modify to suit specific simulation needs.

---

## Installation

### Prerequisites
Ensure you have Python 3.8+ installed.

### Clone the Repository
```bash
git clone https://github.com/HarvestStars/DES_Simulation.git
cd DES_Simulation
```

## Usage
To run a simulation:

- Define your processes and events in Python.
- Use the simpy library to create and manage the simulation environment.
- Register your processes and events, then execute the simulation.

## Examples
Here's a simple example to get you started:
```bash
import simpy

def customer(env, name, counter):
    print(f'{name} arriving at {env.now}')
    with counter.request() as req:
        yield req
        print(f'{name} being served at {env.now}')
        yield env.timeout(5)
        print(f'{name} leaves at {env.now}')

def setup(env, num_counters):
    counter = simpy.Resource(env, num_counters)
    for i in range(3):
        env.process(customer(env, f'Customer {i}', counter))

env = simpy.Environment()
env.process(setup(env, num_counters=2))
env.run(until=20)
```

## Project Structure
- src/: Core implementation of the simulation framework.
- data/: Results of different queuing situations simulated by various models
- visualization/: Plotting of the simulations, like Confidence Interval Bands of various models.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- This project uses the SimPy library for discrete event simulation.
