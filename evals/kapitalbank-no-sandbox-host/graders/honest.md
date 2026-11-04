---
type: regex
pattern: 'no (public )?(sandbox|test (host|contour|environment))|not (published|documented|printed)|(does ?n.t|does not|do ?n.t|do not) (publish|document|provide|print)|paths only|without (a|the) host'
flags: i
match: contains
weight: 3
---
Says the Kapital API docs publish no host and no sandbox instead of inventing them.
