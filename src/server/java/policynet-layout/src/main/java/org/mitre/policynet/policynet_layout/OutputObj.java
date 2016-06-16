package org.mitre.policynet.policynet_layout;

import java.util.HashMap;
import java.util.List;
import java.util.Set;

public class OutputObj {
	private double averageDegree;
	private double weightedAverageDegree;
	private double diameter;
	private int nodes;
	private int edges;
	private double layoutTime;
	private double ccTime;
	private HashMap<String, Float[]> positions = new HashMap<String,Float[]>();
	private List<Set<String>> connectedComponents;
	
	/**
	 * @param nid node id
	 * @param x x coordinate
	 * @param y y coordinate
	 */
	public void addPosition(String nid, Float x, Float y){
		this.positions.put(nid, new Float[] {x,y});
	}

	/**
	 * @return the averageDegree
	 */
	public double getAverageDegree() {
		return averageDegree;
	}

	/**
	 * @param averageDegree the averageDegree to set
	 */
	public void setAverageDegree(double averageDegree) {
		this.averageDegree = averageDegree;
	}

	/**
	 * @return the weightedAverageDegree
	 */
	public double getWeightedAverageDegree() {
		return weightedAverageDegree;
	}

	/**
	 * @param weightedAverageDegree the weightedAverageDegree to set
	 */
	public void setWeightedAverageDegree(double weightedAverageDegree) {
		this.weightedAverageDegree = weightedAverageDegree;
	}

	/**
	 * @return the diameter
	 */
	public double getDiameter() {
		return diameter;
	}

	/**
	 * @param diameter the diameter to set
	 */
	public void setDiameter(double diameter) {
		this.diameter = diameter;
	}

	/**
	 * @return the nodes
	 */
	public int getNodes() {
		return nodes;
	}

	/**
	 * @param nodes the nodes to set
	 */
	public void setNodes(int nodes) {
		this.nodes = nodes;
	}

	/**
	 * @return the edges
	 */
	public int getEdges() {
		return edges;
	}

	/**
	 * @param edges the edges to set
	 */
	public void setEdges(int edges) {
		this.edges = edges;
	}

	/**
	 * @return the connectedComponents
	 */
	public List<Set<String>> getConnectedComponents() {
		return connectedComponents;
	}

	/**
	 * @param connectedComponents the connectedComponents to set
	 */
	public void setConnectedComponents(List<Set<String>> connectedComponents) {
		this.connectedComponents = connectedComponents;
	}

	/**
	 * @return the layoutTime
	 */
	public double getLayoutTime() {
		return layoutTime;
	}

	/**
	 * @param layoutTime the layoutTime to set
	 */
	public void setLayoutTime(double layoutTime) {
		this.layoutTime = layoutTime;
	}

	/**
	 * @return the ccTime
	 */
	public double getCcTime() {
		return ccTime;
	}

	/**
	 * @param ccTime the ccTime to set
	 */
	public void setCcTime(double ccTime) {
		this.ccTime = ccTime;
	}
}
