## Simulation of Whale Warehouse
#### environment: Python3.6, simpy

##### <u>Discreate event simulation</u>

###### Directory structure

> Whale_warehouse
>
> ​----**src**
>
> --------CONSTANT.py : input parameters. of warehouse
>
> ​--------PSB.py : psb robot class
>
> ​--------PSBs.py psb robots composed the fleet class
>
> --------PST.py : pst robot class
>
> ​--------\__init__.py
>
> ​--------cell.py : single storage bin class
>
> ​--------products.py : waiting update
>
> ​--------simulation.py   **Main program**:include simulation flow
>
> ​--------stack.py : 
>
> ​--------test.log : **current result log**
>
> ​--------warehouse.py
>
> ​--------workstation.py
>
> ​----**Thinking**
>
> --------Sim_flowchart.png
>
> --------Sim_scenearios.png
>
> ​--------WhalehouseResult.txt
>
> ​--------flowchart.vsdx

Flow:
>1. Order arrives at poisson process
>2. System  assigns an available and closer robot to the order OR wait in the queue.
>3. PSB robot moves in shortest path
>4. PSB robot fetches the retrieval bin.
>    dedicated storage: pick up the top bin.
>✓✓✓✓shared storage policy: ✓✓✓✓
>            if retrieval bin is on peek: pick up
>            else: reshuffling
>                        ✓✓✓✓ immediate reshuffling ✓✓✓✓
>                             delayed reshuffling
>5. PSB robot transports bin to designated workstation, drop off and pick up a storage bin.
>6. PSB robot transports to storage point. random stack:
>                            at any position zoned stacks: got to the zone determined by turnover.
>7. PSB robot drop off the bin on the top of a randomly stack.
>8. If previous retrieval includes a reshuffling, then returning blocking bins to storage rack.