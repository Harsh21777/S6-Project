### Heuristic H-2 — Resource Utilization Minimization

**Goal.** Minimize the total residual resources across all allocated nodes, improving overall resource utilization.

**Input**
- `N`: set of nodes
- `S`: set of services
- `max_iter`: maximum number of iterations

**Output**
- `q`: number of allocated nodes
- `{S_j}`: subset of services assigned to each node `n_j ∈ N`

---

#### Pseudocode

Algorithm H2(N, S, max_iter)

1.  Sort the node set `N` in descending order by available resources  
2.  `q ← |N|`                                 // current best number of allocated nodes  
3.  `⟨S_1, …, S_|N|⟩ ← ⟨∅, …, ∅⟩`              // best assignment (initially empty)  
4.  `ρ ← Σ_{j=1..p} Σ_{k=1..r} C_{j,k}`       // total residual resources (initial value)

---

5.  for `t` from 1 to `max_iter` do  
6.      `⟨S'_1, …, S'_|N|⟩ ← ⟨∅, …, ∅⟩`       // current assignment for this iteration  
7.      `ρ' ← 0`                              // initialize residual resources for this run  
8.      `S' ← S`                              // reset list of unassigned services  
9.      `N' ← ∅`                              // set of nodes used in this run  

10.     for each node `n_j ∈ N` do  
11.         `ρ' ← ρ' + Σ_{k=1..r} C_{j,k}`     // add node’s total capacity  
12.         for each service `s_i ∈ S` do  
13.             if node `n_j` can host `s_i`  
                (`C_{j,k} ≥ d_{i,k}` for all resources `k`) then  
14.                 `S'_j ← S'_j ∪ {s_i}`      // assign service to node  
15.                 `S'  ← S'  \ {s_i}`        // remove service from pool  
16.                 `N'  ← N'  ∪ {n_j}`        // mark node as allocated  
17.                 `ρ' ← ρ' - Σ_{k=1..r} d_{i,k}` // update total residual resources  
18.             end if  
19.         end for  
20.     end for  

---

21.     if `(q > |N'|) and (ρ > ρ')` then  
22.         `⟨S_1, …, S_|N|⟩ ← ⟨S'_1, …, S'_|N|⟩`  // save current best solution  
23.         `⟨q, ρ⟩ ← ⟨|N'|, ρ'⟩`                 // update best metrics  
24.     end if  
25.  end for  

26.  return (`q`, `S_1`, …, `S_|N|`)              // best solution found