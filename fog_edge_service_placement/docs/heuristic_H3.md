### Heuristic H-3 — Hop Minimization

**Goal.**  
Minimize the total number of hops in the communication path between consecutively deployed services, favoring proximity between nodes while maintaining resource feasibility.

**Input**
- `N`: set of nodes  
- `S`: ordered set of services (forming a chain)  
- `M`: hop-count matrix between nodes, where `M[i][j] = δ_{i,j}`  

**Output**
- `q`: number of allocated nodes  
- `{S_j}`: subset of services assigned to each node `n_j ∈ N`

---

#### Pseudocode

Algorithm H3(N, S, M)

1.  `q ← |N|`                                   // total number of nodes  
2.  `⟨S₁, …, S_|N|⟩ ← ⟨∅, …, ∅⟩`                // initialize best allocation  
3.  `Δ ← Σ_{j₁=1..p} Σ_{j₂=1..p} Σ_{i=2..m} δ_{j₁,j₂}`  // initialize with max possible hops  

---

4.  for each starting node `n_j₁ ∈ N` do  
5.      `N' ← ∅`                                // allocated nodes for this attempt  
6.      `S' ← ∅`                                // services allocated in this attempt  
7.      `n_j₂ ← n_j₁`                           // current node to place next service  
8.      `Δ' ← 0`                                // hop count for this attempt  

9.      for each service `s_i ∈ S` do  
10.         if `n_j₂` has enough resources for `s_i` (`C_{j₂,k} ≥ d_{i,k}` for all k) then  
11.             `N' ← N' ∪ {n_j₂}`              // mark node as used  
12.             `S' ← S' ∪ {s_i}`               // assign service to node  
13.         else  
14.             `L ← Ω(M[n_j₂])`                // list of neighboring nodes sorted by hop count  
15.             for each `n_j₂ ∈ L` do  
16.                 if `C_{j₂,k} ≥ d_{i,k}` for all k then  
17.                     break                    // select first feasible neighbor  
18.                 end if  
19.             end for  
20.             `Δ' ← Δ' + δ_{n_j₁,n_j₂}`       // update hop count  
21.             `n_j₁ ← n_j₂`                   // move to next node  
22.         end if  
23.      end for  

24.     if `(q > |N'|)` and `(Δ > Δ')` then  
25.         `⟨S₁, …, S_|N|⟩ ← ⟨S'₁, …, S'_|N|⟩`  // update best allocation  
26.         `⟨q, Δ⟩ ← ⟨|N'|, Δ'⟩`                 // update best metrics  
27.     end if  
28. end for  

29. return (`q`, S₁, …, S_|N|`)