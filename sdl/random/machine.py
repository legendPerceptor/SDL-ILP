import networkx as nx
import numpy as np

from numpy.random import RandomState
from sdl.lab import Operation, Machine
from typing import List, Set, Optional, Union


def bipartite_machine_operation_matching(
        num_machines: int,
        num_operations: int,
        avg_degree: float,
        random_state: RandomState = None,
        return_graph: bool = False
) -> Union[list[Machine], nx.Graph]:
    if random_state is None:
        random_state = RandomState()

    if avg_degree < 1:
        raise ValueError("`avg_degree` must be at least 1.")
    machine_nodes = [f"m-{mach}" for mach in range(num_machines)]
    operation_nodes = [f"o-{op}" for op in range(num_operations)]
    g = nx.Graph()
    g.add_nodes_from(machine_nodes, bipartite=0)
    g.add_nodes_from(operation_nodes, bipartite=1)

    # Initialize the first batch of edges, ensuring that all machines and operations
    # are covered by at least 1 pair. The split in logic is to handle cases where there
    # are fewer machines OR fewer operations to have a clean 1:1 matching.
    if num_machines < num_operations:
        mdx = 0
        for op_node in operation_nodes:
            m_node = machine_nodes[mdx % len(machine_nodes)]
            g.add_edge(m_node, op_node)
            mdx += 1
    else:
        odx = 0
        for m_node in machine_nodes:
            op_node = operation_nodes[odx % len(operation_nodes)]
            g.add_edge(m_node, op_node)
            odx += 1

    # Add new random edges between machines and operations if the average degree
    # threshold is not met. However, please keep in mind that this will be limited
    # based on the number of possible machine-operation matches.
    needed_edges = avg_degree * g.number_of_nodes()
    edges_to_add = needed_edges - g.number_of_edges()
    possible_edges = num_operations * num_machines
    for e in range(edges_to_add):
        if e + g.number_of_edges() >= possible_edges:
            break
        done = False
        while not done:
            m_node = random_state.choice(machine_nodes)
            op_node = random_state.choice(operation_nodes)
            if not g.has_edge(m_node, op_node):
                g.add_edge(m_node, op_node)
                done = True

    if return_graph:
        return g

    machines = []
    for m_idx, m_node in enumerate(machine_nodes):
        operations = set([op_node for op_node in g.neighbors(m_node)])  # FIXME: Convert to Operation objects.
        machines.append(Machine(m_idx, m_node, operations))
    return machines


def create_machine_partition(
        operations: List[Operation],
        p: int,
        m: int,
        random_state: Optional[RandomState] = None
):
    if random_state is None:
        random_state = RandomState()
    if p > m:
        raise ValueError('Total number of machines should be larger than partition number')
    if p > len(operations):
        raise ValueError('Number of partition should be smaller than total number of operation_pool')

    split_operations = np.array_split(operations, p)
    machines = []
    operations_to_machines = {op.opcode: set() for op in operations}
    for machine_id, operation_set in enumerate(split_operations):
        machines.append(Machine(machine_id + 1, f'M_{machine_id + 1}', set(operation_set)))
        for operation in operation_set:
            operations_to_machines[operation.opcode].add(machine_id + 1)

    remaining_machines = m - p
    for i in range(0, remaining_machines, 1):
        n_operations = random_state.randint(1, len(operations) // 2)
        cur_operations = random_state.choice(operations, n_operations, replace=False)
        machines.append(Machine(p + 1 + i, f'M_{p + 1 + i}', set(cur_operations)))
        for operation in cur_operations:
            operations_to_machines[operation.opcode].add(p + 1 + i)
    return machines, operations_to_machines


if __name__ == "__main__":
    # a = [1, 2, 1, 3, 3, 3]
    # b = [2, 2, 2, 1, 4, 2]
    # g = nx.algorithms.bipartite.configuration_model(a, b)
    # top = nx.bipartite.sets(g)[0]

    def avg_degree(g: nx.Graph):
        return g.number_of_edges() / g.number_of_nodes()


    g = bipartite_machine_operation_matching(5, 4, 1)
    print(f"Avg. Degree: {avg_degree(g)}")
    top = {node for (node, data) in g.nodes(data=True) if data["bipartite"] == 0}
    pos = nx.bipartite_layout(g, top)
    nx.draw(g, pos=pos)
    plt.show()
