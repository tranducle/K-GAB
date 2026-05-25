// Cypher Schema Import for K-GAB Physics Curriculum Graph

// 1. Create Constraints
CREATE CONSTRAINT FOR (c:CurriculumStandard) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT FOR (l:PhysicalLaw) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT FOR (m:Misconception) REQUIRE m.id IS UNIQUE;

// 2. Create Curriculum Standard Nodes
CREATE (c1:CurriculumStandard {
  id: "PHYS_G10_ME_01",
  code: "PHYS-G10-ME-01",
  grade: 10,
  topic: "Newtonian Mechanics",
  description: "Biểu diễn và vận dụng Định luật II Newton về động lực học chất điểm"
});

CREATE (c2:CurriculumStandard {
  id: "PHYS_G11_EM_01",
  code: "PHYS-G11-EM-01",
  grade: 11,
  topic: "Electromagnetism",
  description: "Xác định suất điện động cảm ứng trong thanh dẫn chuyển động vuông góc với từ trường"
});

CREATE (c3:CurriculumStandard {
  id: "PHYS_G12_NP_01",
  code: "PHYS-G12-NP-01",
  grade: 12,
  topic: "Nuclear Physics",
  description: "Vận dụng công thức chu kỳ bán rã của chất phóng xạ để tính khối lượng còn lại"
});

// 3. Create Physical Law Nodes
CREATE (l1:PhysicalLaw {
  id: "LAW_NEWTON_2",
  name: "Định luật II Newton",
  formula_latex: "F = m * a",
  variables: ["F:Lực:N", "m:Khối lượng:kg", "a:Gia tốc:m/s^2"]
});

CREATE (l2:PhysicalLaw {
  id: "LAW_FARADAY_MOTION",
  name: "Suất điện động cảm ứng chuyển động",
  formula_latex: "e = B * l * v * \\sin\\alpha",
  variables: ["e:Suất điện động:V", "B:Cảm ứng từ:T", "l:Chiều dài thanh:m", "v:Vận tốc:m/s", "alpha:Góc hướng:rad"]
});

CREATE (l3:PhysicalLaw {
  id: "LAW_HALF_LIFE",
  name: "Định luật phóng xạ",
  formula_latex: "m_t = m_0 * 2^(-t / T)",
  variables: ["m_t:Khối lượng còn lại:g", "m_0:Khối lượng ban đầu:g", "t:Thời gian phân rã:s", "T:Chu kỳ bán rã:s"]
});

// 4. Create Misconception Nodes
CREATE (m1:Misconception {
  id: "MC_ARISTOTELIAN_IMPETUS",
  name: "Lực duy trì chuyển động",
  description: "Học sinh tin rằng vật chuyển động thẳng đều thì phải có lực kéo lớn hơn lực cản.",
  algebraic_slip_formula: "F = m * v"
});

CREATE (m2:Misconception {
  id: "MC_TRIG_CONFUSION",
  name: "Nhầm lẫn hàm lượng giác",
  description: "Học sinh nhầm lẫn giữa sin và cos khi tính suất điện động của thanh dẫn cắt đường sức từ.",
  algebraic_slip_formula: "e = B * l * v * \\cos\\alpha"
});

CREATE (m3:Misconception {
  id: "MC_LINEAR_DECAY",
  name: "Phóng xạ tuyến tính",
  description: "Học sinh tin rằng tốc độ phóng xạ giảm đều tuyến tính theo thời gian thay vì hàm mũ.",
  algebraic_slip_formula: "m_t = m_0 * (1 - t / T)"
});

// 5. Create Relational Edges
MATCH (c:CurriculumStandard {id: "PHYS_G10_ME_01"}), (l:PhysicalLaw {id: "LAW_NEWTON_2"}) CREATE (c)-[:REQUIRES]->(l);
MATCH (c:CurriculumStandard {id: "PHYS_G11_EM_01"}), (l:PhysicalLaw {id: "LAW_FARADAY_MOTION"}) CREATE (c)-[:REQUIRES]->(l);
MATCH (c:CurriculumStandard {id: "PHYS_G12_NP_01"}), (l:PhysicalLaw {id: "LAW_HALF_LIFE"}) CREATE (c)-[:REQUIRES]->(l);

MATCH (l:PhysicalLaw {id: "LAW_NEWTON_2"}), (m:Misconception {id: "MC_ARISTOTELIAN_IMPETUS"}) CREATE (l)-[:VIOLATES]->(m);
MATCH (l:PhysicalLaw {id: "LAW_FARADAY_MOTION"}), (m:Misconception {id: "MC_TRIG_CONFUSION"}) CREATE (l)-[:VIOLATES]->(m);
MATCH (l:PhysicalLaw {id: "LAW_HALF_LIFE"}), (m:Misconception {id: "MC_LINEAR_DECAY"}) CREATE (l)-[:VIOLATES]->(m);
