### Heuristic H-1 — Node Minimization

**Goal.** Minimize the number of allocated nodes by iteratively assigning services to nodes, exploring multiple randomized service orders and keeping the best solution.

**Input**
- `N`: set of nodes
- `S`: set of services
- `max_iter`: maximum number of iterations

**Output**
- `q`: number of allocated nodes
- `{S_j}`: subset of services assigned to each node `n_j ∈ N`

---

#### Pseudocode

Algorithm H1(N, S, max_iter)

1.  Sort the node set `N` in descending order by available resources
2.  `q ← |N|`                        // current best number of allocated nodes
3.  `⟨S_1, …, S_|N|⟩ ← ⟨∅, …, ∅⟩`    // best assignment (initially empty)

4.  for `t` from 1 to `max_iter` do           // iterate with multi-start
5.      `⟨S'_1, …, S'_|N|⟩ ← ⟨∅, …, ∅⟩`       // current assignment for this run
6.      `S' ← S`                              // services not yet assigned
7.      `N' ← ∅`                              // set of nodes used in this run
8.
9.      for each node `n_j ∈ N` do           // check each node in order
10.         `S'_j ← ∅`                       // auxiliary set of services for node j
11.         `S^o ← ω(S)`                     // random permutation of S
12.
13.         for each service `s_i ∈ S^o` do
14.             if node `n_j` can host `s_i`
15.                i.e., `C_{j,k} ≥ d_{i,k}` for all resources k
16.             then
17.                 `S'_j ← S'_j ∪ {s_i}`     // assign service to node j
18.                 `S'  ← S'  \ {s_i}`       // remove from unassigned set
19.                 `N'  ← N' ∪ {n_j}`        // mark node as allocated
20.             end if
21.         end for
22.     end for
23.
24.     // If the current solution uses fewer nodes, update the best one
25.     if `q > |N'|` then
26.         `⟨S_1, …, S_|N|⟩ ← ⟨S'_1, …, S'_|N|⟩`
27.         `q ← |N'|`
28.     end if
29. end for
30.
31. return (`q`, `S_1`, …, `S_|N|`)